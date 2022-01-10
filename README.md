# Auto chart generator
Tries to make a FnF chart based on raw midi notes.
It will take a look at the midi notes for a character,
and attempt to generate a chart based on it.

Your midi notes are literally the notes to the song.
It is NOT a "midi" of the chart. This is not Emma/PrincessMTH's SNIFF or NyxTheShield's Midi2FNF. This means your
midi notes can span between C0 and C8. I'm likely
going to need to create a version that has the same
capabilities of the two other programs I mentioned.

Yes, this can generate FnF charts without the pain
of you having to chart.

## Setting up your midi file
Remember FL Studio counts MIDI channels from 1 while everyone else (excluding UIs that count from 1) counts from 0.

* Your MIDI channel 0 are your enemy notes.
* Your MIDI channel 1 are your BF notes.
* All other MIDI channels are ignored.
* BPM is automatically detected.
* BPM changes are not supported. Don't try.
* BF/Enemy camera/MustHitSection is automatically handled in the program.

## Running this program
1. Open ``midi4.py`` or the ``.exe`` file I included in the release if there is any.
2. Open the midi file it prompts you to open.
3. Answer all questions.
4. Afterwards, the program will close, and a chart will be generated in the same directory as this ``.py`` or ``.exe``  file.

## Requirements
You need the latest version of ``easygui`` (a python package)
to run this if you're using the ``.py`` file.

If you are running from ``.exe``, you don't need to
install anything. However, there are people who don't like
running ``.exe`` files from random people over the internet,
so I've included the source code if you want to run from that.

### How does this program actually works?
For each character:
1. Check the last note (generate a random note if it is the first note in the chart).
2. If the last note's pitch is higher, reflect that in the chart (same chance that next arrow is 1 or 2 higher).
3. If the last note's pitch is lower, reflect that in the chart (same chance that next arrow is 1 or 2 lower).
4. If the last note's pitch is the same, reflect that in the chart (chance for same arrow or chance for random note).

Arrows always wrap around. This means one higher than the right arrow is the left arrow.

For each section:
* Camera focuses at character who has at least 70% of the notes from the sum of both character's notes in a section.
* If that isn't the case, then the camera will always alternate.

## Disclaimer
* This is a side project; source code is
really messy.
* Please don't actually use this to chart an
ambitious mod. While this may chart songs quickly and
accurately (based on timings) the patterns may not be
fun to play. I did not test this.
