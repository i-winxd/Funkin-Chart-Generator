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

## Running this program (FOLLOW INSTALLATION INSTRUCTIONS)

**PLEASE FOLLOW THIS TUTORIAL. TRY NOT TO DOWNLOAD THE EXE FILE UNLESS YOU ARE WILLING TO TAKE RISKS. DEPENDENCIES ARE BELOW**
https://gist.github.com/i-winxd/0af33288536c155ac06690d3953156a4

(Windows only) To quickly run this app, click on `funkinChartGenerator.bat`. This will only work once you've
installed Python and have successfully ran `pip install mido` before. What this file does is open command prompt,
where the current working directory is the folder the `.bat` file is in, and run the command `py main.py`.

#### Funkin' Chart Generator specific steps

In `settings.json`, set the values to what you want them to be. Then, run `main.py` and select the **MIDI**
file it prompts you to open. The program will spit a new file out which should match the name of your song (not 
the name of the MIDI file).

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
