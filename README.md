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
* All other MIDI channels are ignored.
* BPM is automatically detected.
* **BPM changes are not supported. Don't try.**
* BF/Enemy camera/MustHitSection is automatically handled in the program.
* **A sustain note is any note that lasts more than 2 steps (8th note) or has a velocity of less than 50% the moment it starts.**

To create and export midis in FL Studio, create MIDI out tracks. When you export, it will export everything in the midi out tracks. Remember to set the channels in the MIDI out tracks.
The program may not work if either bf or the enemy does not have any notes.

## Running this program (FOLLOW INSTALLATION INSTRUCTIONS)
Using the exe will likely activate your antivirus, so you should be using the ``.py`` file. If you're running the exe, just open the exe file. MAKE SURE IT IS IN A FOLDER AS IT WILL EXPORT EVERYTHING IN THE SAME FOLDER AS THIS EXE FILE!!!

If you're running the .py file, make sure all requirements below are met.
1. Open ``main.py`` using python 3.10. Install python 3.10 **THROUGH THE WINDOWS 10 APP STORE (not anywhere else unless you know what you're doing)**
2. If you're running this program for the first time enter these in your command prompt line by line:

```
pip install easygui
pip install mido
```
3. Open command prompt in the folder you dragged ``main.py`` to. ``midi2.py`` and ``midi3.py`` must be in the same folder as well, so I would drag everything to a seperate folder. You can open command prompt in a folder by literally typing ``cmd`` in whatever this thing is provided your folder is focused:

![image](https://user-images.githubusercontent.com/31808925/154206731-eb74d2a8-27fa-42ac-8b28-61c58eab11c3.png)

4. Open the midi file it prompts you to open. (If it doesn't, rerun the app)
5. Answer all questions.
6. Afterwards, the program will close, and a chart will be generated in the same directory as this ``.py`` file.

### How does this program actually work?
For each character:
1. Check the last note (generate a random note if it is the first note in the chart).
2. If the last note's pitch is higher, reflect that in the chart (insert note in chart righter than previous. Distance is max. 2 based on music note difference).
3. If the last note's pitch is lower, reflect that in the chart (insert note in chart lefter than previous).
4. If the last note's pitch is the same, reflect that in the chart (chance for same arrow or chance for random note).

Arrows always wrap around. This means one higher than the right arrow is the left arrow.

For each section:
* Camera focuses at character who has at least 65% of the notes from the sum of both character's notes in a section.
* If that isn't the case, then the camera will always alternate.

## Disclaimer
* This is a side project; source code is
really messy.
* Please don't actually use this to chart an
ambitious mod. While this may chart songs quickly and
accurately (based on timings) the patterns may not be
fun to play. I did not test this.
