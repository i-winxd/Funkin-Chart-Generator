"""
Determine the auto chart maker

Channel 0 is EN
Channel 1 is BF

Autodetect sections:
    - Section numbers count from zero
    - If 65% of the notes are from a character, it will focus on them
    - Else, it will always do the switch
"""
from dataclasses import dataclass
# from pprint import pprint
from pprint import pprint
import midi2 as mid2
import midi3 as mid3
import random
import json
import easygui
import logging

# logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

# channel 0 is always EN's notes.
# all the notes must be in order.
# a note sequence is a list of notes in a channel.


DISABLE_PROMPTS = False
SWAP_BF_EN = False


@dataclass(frozen=True)
class Preferences:
    """A class representing preferences
    Representation invariants:
        - 0 <= jack_mode <= 3
    """
    jack_mode: int  # the chance out of 3 for jacks to be skipped.
    note_tolerance: int  # the % of notes required for camera to focus on character


def process_notes(channel_data, spb: float, prefs: Preferences):
    """Determine arrow position of notes for a character.
    Channel data must be in time, pitch, velocity, dur format
    """
    chart_notes = []
    prev_note = [0, 60, 100, 0.0]
    prev_pitch = prev_note[1]
    cur_arrow = random.randint(0, 3)
    for note in channel_data:
        logging.debug(f'---------- previous note is {cur_arrow}')
        cur_pitch = note[1]
        diff = cur_pitch - prev_pitch

        if cur_pitch < prev_pitch:
            cur_arrow = (cur_arrow - one_or_two_seed(diff)) % 4
            logging.debug(f'arrow down due to {cur_pitch} < {prev_pitch}')
        elif cur_pitch > prev_pitch:
            cur_arrow = (cur_arrow + one_or_two_seed(diff)) % 4
            logging.debug(f'arrow up due to {cur_pitch} > {prev_pitch}')
        elif random.randint(1, 3) <= prefs.jack_mode:
            logging.debug(f'arrow randomized due to {cur_pitch} == {prev_pitch}')
            cur_arrow = (cur_arrow + random.randint(-2, 2)) % 4
        else:
            logging.debug(f'arrow same due to {cur_pitch} == {prev_pitch}')

        # account for sustains
        # sus_length = 0 if note[2] >= 60 else note[3]
        if note[2] < 60 or note[3] > (spb / 2) + 0.0001:
            sus_length = note[3] * 0.85 * 1000
        else:
            sus_length = 0
        chart_notes.append([note[0] * 1000, cur_arrow, sus_length])
        prev_pitch = cur_pitch
        # prev_note = note.copy()
    return chart_notes


def one_or_two(chance: int) -> int:
    """Return 1 or 2; chance of 2 represented by chance out of 100.
    """
    ran = random.randint(0, 100)
    if chance >= ran:
        return 2
    else:
        return 1


def one_or_two_seed(seed: int) -> int:
    """Return 1 or 2; chance of 2 represented by seed.
    """
    seed = abs(seed)
    seed_map = {0: 0, 1: 1, 2: 1, 3: 1, 4: 2, 5: 3, 6: 4}
    if seed <= 6:
        chance = seed_map[seed]
    else:
        chance = 4
    rand = random.randint(0, 6)
    # the greater the chance, the higher that it is a two
    # meaning
    if chance >= rand:
        return 2
    else:
        return 1


def main(path: str):
    pm = mid2.process_midi(path)
    spb = mid2.obtain_spb(path)
    # print(spb)
    bpm = round(60 / spb, 3)
    print('Your BPM is ' + str(bpm))
    if not DISABLE_PROMPTS:
        p1 = input('Player 1? (Likely bf): ')
        p2 = input('Player 2? (Enemy): ')
        gf = input('gfVersion? (Likely gf): ')
        song = input('Song name?: ')
        stage = input('Stage name? ')
        needs_voices_input = input('needs voices? (t/f, default t): ')
        if needs_voices_input.lower() == 'f':
            needs_voices = False
            print('You choose FALSE for above.')
        else:
            needs_voices = True
        # valid_score = True
        scroll_speed = float(input('Scroll speed?: '))
    else:
        p1, p2, gf, song, stage, needs_voices, scroll_speed = 'bf', 'dad', 'gf', \
                                                              'testsong', 'stage', 'True', '2.4'

    full_mid_data = mid3.main(pm)
    prefs = Preferences(0, 65)
    try:
        full_note_list_en = process_notes(full_mid_data[0], spb, prefs)
    except IndexError:
        full_note_list_en = []
    try:
        full_note_list_bf = process_notes(full_mid_data[1], spb, prefs)
    except IndexError:
        full_note_list_bf = []
    # pprint(full_note_list)
    sectioned_en_list = split_into_sections(full_note_list_en, spb)
    sectioned_bf_list = split_into_sections(full_note_list_bf, spb)

    if SWAP_BF_EN:
        sectioned_bf_list, sectioned_en_list = sectioned_en_list, sectioned_bf_list

    # ensure both lists are the same length
    if len(sectioned_en_list) != len(sectioned_bf_list):
        len_diff = abs(len(sectioned_bf_list) - len(sectioned_en_list))
        if len(sectioned_en_list) < len(sectioned_bf_list):
            for _ in range(0, len_diff):
                sectioned_en_list.append([])
        if len(sectioned_en_list) > len(sectioned_bf_list):
            for _ in range(0, len_diff):
                sectioned_bf_list.append([])

    musthit = True
    json_notes = []
    for en_section, bf_section in zip(sectioned_en_list, sectioned_bf_list):
        sec_notes, musthit = compare_sections(en_section, bf_section, musthit, prefs)
        json_notes.append(
            {"sectionNotes": sec_notes, "lengthInSteps": 16, "mustHitSection": musthit})
    # pprint(json_notes)

    full_json = {"song": {"player1": p1, "player2": p2, "gfVersion": gf,
                          "notes": json_notes, "stage": stage, "needsVoices": needs_voices,
                          "validScore": True, "bpm": bpm, "speed": scroll_speed, "song": song}}

    json_name = song + '-hard.json'
    if DISABLE_PROMPTS:
        pprint(full_json)
    else:
        with open(json_name, 'w') as json_export:
            json.dump(full_json, json_export)


def split_into_sections(notes: list, spb: float):
    """Split a list of note data into sections. It doesn't matter
    what format notes is in; the first index must be time in seconds.
    Time, pitch, vel, dur"""
    section_length = spb * 4
    full_note_data = {}
    for note in notes:
        note_section = ((note[0] / 1000) + 0.0001) // section_length
        if note_section not in full_note_data:
            full_note_data[note_section] = []
        full_note_data[note_section].append(note)
    highest_channel = max(int(mm) for mm in full_note_data.keys()) + 1
    isolated_section_list = [[] for _ in range(0, highest_channel)]
    for key, item in full_note_data.items():
        isolated_section_list[int(key)] = item
    return isolated_section_list


def compare_sections(en_section: list,
                     bf_section: list, prev_musthit: bool, prefs: Preferences) -> \
        tuple[list, bool]:
    """Return
    CombinedSectionList, MustHitSection
    """
    if len(en_section) != 0:
        percent_bf = (len(bf_section) / len(en_section)) * 100
    elif len(bf_section) == 0:
        percent_bf = 50
    else:
        percent_bf = 100

    if percent_bf >= prefs.note_tolerance:
        must_hit = True
    elif prefs.note_tolerance >= percent_bf >= (100 - prefs.note_tolerance):
        must_hit = not prev_musthit
    else:
        must_hit = False
    unsorted_combined_sections = []
    if must_hit:  # if must_hit is true or if camera points to bf
        for en_note in en_section:
            unsorted_combined_sections.append([en_note[0], en_note[1] + 4, en_note[2]])
        for bf_note in bf_section:
            unsorted_combined_sections.append([bf_note[0], bf_note[1], bf_note[2]])
    else:  # if must_hit is false or if cam points to en
        for en_note in en_section:
            unsorted_combined_sections.append([en_note[0], en_note[1], en_note[2]])
        for bf_note in bf_section:
            unsorted_combined_sections.append([bf_note[0], bf_note[1] + 4, bf_note[2]])
    sorted_combined_sections = sorted(unsorted_combined_sections, key=lambda x: (x[0], x[1]))
    return sorted_combined_sections, must_hit


if __name__ == '__main__':
    path = easygui.fileopenbox(msg='Select the *.mid file you want to open',
                               filetypes=["*.mid"])
    print('File selected')
    main(path)
