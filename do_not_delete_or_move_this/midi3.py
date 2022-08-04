"""Bruh moment
"""
# from pprint import pprint
from pprint import pprint
from typing import Union

from do_not_delete_or_move_this import midi2 as mid


def main(processed_mid_data):
    lm = isolate_channels(processed_mid_data)
    # pprint(lm)
    jm = format_indv_pitch_bulk(lm)
    # pprint(jm)
    return jm


def isolate_channels(mid_data: list[list[str, int, Union[int, float], int]]) -> list[list]:
    """Isolate midi channel.
    What it returns:
    [[channel data[note data]], [channel data[note data]]]
    """
    isolated_so_far = {}
    for note in mid_data:
        if note[3] not in isolated_so_far:
            isolated_so_far[note[3]] = []
        isolated_so_far[note[3]].append(note)
    highest_channel = max(int(mm) for mm in isolated_so_far.keys()) + 1
    isolated_channel_list = [[] for _ in range(0, highest_channel)]
    for key, item in isolated_so_far.items():
        isolated_channel_list[int(key)] = item
    return isolated_channel_list


def format_indv_pitch_bulk(mid_data) -> list[list[list]]:
    """Start with the entire thing
    end with the entire thing
    """
    outer_export = []
    for channel in mid_data:
        channel_pitch_export = []
        seperated_pitch_data = separate_pitches(channel)
        for individual_pitch in seperated_pitch_data:
            indv_p = format_channel_indv_pitch(individual_pitch)
            channel_pitch_export.append(indv_p)
        channel_all_export = []
        for indv_pitch in channel_pitch_export:
            for indv_note in indv_pitch:
                channel_all_export.append(indv_note)
        sorted_channel_all = sorted(channel_all_export, key=lambda x: (x[0], x[1]))
        outer_export.append(sorted_channel_all)
    return outer_export


def separate_pitches(channel_data) -> list[list]:
    full_note_data = {}
    for note in channel_data:
        if note[1] not in full_note_data:
            full_note_data[note[1]] = []
        full_note_data[note[1]].append(note)
    # generate it in complete random.
    export_list = []
    for _, item in full_note_data.items():
        export_list.append(item)
    return export_list


def format_channel_indv_pitch(channel_data):
    """Will output:
    [time, pitch, vel, dur]
    Cases:
        - First note is off? Don't count it
        - Last note is on? Don't count it.
        - Two ons in a row? Don't count the second one.
    """
    notes_so_far = []
    last_on_note_data = []
    prev_note_state = ''
    for note in channel_data:
        try:
            if prev_note_state == '' or prev_note_state == 'note_off':
                # requires that notes be ON or skipped
                if note[0] == 'note_on':
                    last_on_note_data = [note[2], note[1], note[4]]  # time, pitch, vel
                    prev_note_state = 'note_on'
                else:
                    continue
            if prev_note_state == 'note_on':
                # requires that notes be OFF or skipped.
                if note[0] == 'note_off':
                    dur = note[2] - last_on_note_data[0]
                    new_data = last_on_note_data + [dur]
                    notes_so_far.append(new_data)
                    prev_note_state = 'note_off'
                else:
                    continue
        except IndexError:
            continue
    return notes_so_far


if __name__ == '__main__':
    pm = mid.process_midi('tmf.mid')
    # pprint(pm)
    pprint(main(pm))
