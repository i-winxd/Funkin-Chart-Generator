# Auto chart generator

**THIS HAS A USER INTERFACE SEE THE RELEASES ON THE RIGHT THIS
CAN BE DOWNLOADED AS JUST ONE EXE FILE**

https://github.com/i-winxd/Funkin-Chart-Generator/releases/

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

* Your MIDI channel 0 are your enemy notes. **(FL Studio channel 1)**
* Your MIDI channel 1 are your BF notes. **(FL Studio channel 2)**
* If you did that in the wrong order, there's an option to swap that.
* All other MIDI channels are ignored.
* BPM is automatically detected.
* **BPM changes are not supported. Don't try.**
* BF/Enemy camera/MustHitSection is automatically handled in the program.
* **A sustain note is any note that lasts more than 2 steps (8th note) or has a velocity of less than 50% the moment it starts.**

To create and export midis in FL Studio, create MIDI out tracks. When you export, it will export everything in the midi out tracks. Remember to set the channels in the MIDI out tracks.
The program may not work if either bf or the enemy does not have any notes.

## Installation

Go to releases and download the zip file over there. Download the correct one. Then, extract everything there to its own folder. Then, run the EXE file.

Field meanings

- Jack skip probability: `jackMode`/3 chance on every "jack" (two same consecutive notes) to make it not a jack anymore
    - set to 3 to eliminate jacks
- Percentage required: for each section, % of notes needed on one side for that section to be that character's section
<!--
#### Funkin' Chart Generator specific steps

In `settings.json`, set the values to what you want them to be. Then, run `chart_gen.py` and select the **MIDI**
file it prompts you to open. The program will spit a new file out which should match the name of your song (not 
the name of the MIDI file).

Some special fields:

- `jackMode`: `jackMode`/3 chance on every "jack" (two same consecutive notes) to make it not a jack anymore (default 0)
    - set to 3 to eliminate jacks
- `percentageRequired`: for each section, % of notes needed on one side for that section to be that character's section (default 75)
-->


### How does this program actually work?
For each character:
1. Check the last note (generate a random note if it is the first note in the chart).
2. If the last note's pitch is higher, reflect that in the chart (insert note in chart righter than previous. Distance is max. 2 based on music note difference).
3. If the last note's pitch is lower, reflect that in the chart (insert note in chart lefter than previous).
4. If the last note's pitch is the same, reflect that in the chart (chance for same arrow or chance for random note).

Arrows always wrap around. This means one higher than the right arrow is the left arrow.

For each section:
* Camera focuses at character who has at least 75% of the notes from the sum of both character's notes in a section.
* If that isn't the case, then the camera will always alternate.

## Disclaimer
* This is a side project; source code is
really messy.
* Please don't actually use this to chart an
ambitious mod. While this may chart songs quickly and
accurately (based on timings) the patterns may not be
fun to play. I did not test this.

## Running this programatically

Read `gen_ui.py` assuming `FCGInputs.get_instance_from_ui` just returns what
you selected in the UI
