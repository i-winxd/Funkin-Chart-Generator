from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from chart_gen import process
from ui import DataclassUI

@dataclass
class FCGInputs(DataclassUI):
    path_to: Path = field(default=Path(""),metadata={'title': 'Select MIDI file', 'filetypes':[('MIDI Files', '*.mid')]})
    jack_mode: int = field(default=0, metadata={'title': 'Jack skip probability\nProbability out of 3 that a jack\ngets skipped (from 0-3), integers only'})
    percentage_required: int = field(default=70, metadata={'title': 'Percentage Required\nIn a section, these notes in % must be owned\nby a character for the camera to focus on them.\nIf neither character meets this,\nthe camera always alternates.\n(from 0-100, integers only)'})
    p1: str = field(default="bf", metadata={'title': 'Player 1\nCharacter usually on the right'})
    p2: str = field(default="dad", metadata={'title': 'Player 2\nCharacter usually on the left'})
    gf: str = field(default="gf", metadata={"title": "GF\nCharacter usually on the middle"})
    song: str = field(default="", metadata={'title': 'Song\nName of the song\nThe JSON file will be named this'})
    stage: str = field(default="", metadata={'title': 'Stage\nName of the stage'})
    needs_voices: bool = field(default=True, metadata={'title': 'Needs voices\n(Just set this to true)'})
    scroll_speed: float = field(default=2, metadata={'title': 'Scroll speed'})
    swap_bf_en_2: bool = field(default=False, metadata={'title': "Swap P1 and P2's notes\nIn case the MIDI was\nin the wrong order"})


def cc(c:FCGInputs)->Optional[str]:
    if c.path_to.__str__() == ".":
        return "You did not select a MIDI file"
    elif c.song == "":
        return "Song name must be populated"
    elif not (0 <= c.jack_mode <= 3):
        return "Jack mode must be from 0-3 inclusive"
    elif not (0 <= c.percentage_required <= 100):
        return "Percentage required must be from 0-100 inclusive"
    else:
        return None

if __name__ == "__main__":
    fcg_inputs = FCGInputs.get_instance_from_ui(title="Funkin' chart generator", desc="Generate a FnF chart from a MIDI entirely.\nYou know the drill, MIDI channel 0 (FL 1) is enemy, MIDI channel 1 (FL 2) is BF\nNote that FL counts channels from 1, beware\nBPM is automatically detected\nBPM changes are not supported\nThe notes in each channel are literally\nfrom the song, the arrow positions are auto", custom_check=cc)
    
    process(path_to=str(fcg_inputs.path_to),
            jack_mode=fcg_inputs.jack_mode,
            percentage_required=fcg_inputs.percentage_required,p1=fcg_inputs.p1,p2=fcg_inputs.p2,gf=fcg_inputs.gf,song=fcg_inputs.song,stage=fcg_inputs.stage,needs_voices=fcg_inputs.needs_voices,scroll_speed=fcg_inputs.scroll_speed,swap_bf_en2=fcg_inputs.swap_bf_en_2)
    