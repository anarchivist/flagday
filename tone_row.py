import copy
from typing import Literal, List
from random import sample

import abjad # pyright: ignore[reportMissingImports]

BASE_ROW : List = list(range(12))

# convenenience method to return a randomized row
def random_tone_row() -> abjad.TwelveToneRow: # pyright: ignore[reportArgumentType]
    randomized_row = sample(BASE_ROW, len(BASE_ROW))
    return abjad.TwelveToneRow(items=randomized_row)

# reformat a string, Pitch, or PitchClass for the RTTTL
# TODO: use abjad's respelling functionality because this is hacky
def reformat_to_sharps(pitch: str | abjad.Pitch | abjad.PitchClass) -> str:
    if isinstance(pitch, abjad.PitchClass):
        pitch = pitch.pitch_class_label() # type: ignore[attr-defined]
    elif isinstance(pitch, abjad.Pitch):
        pitch = pitch.pitch_class().pitch_class_label()  # type: ignore[attr-defined]
    lowercase = pitch.lower()

    match lowercase:
        case "ab":
            return "g#"
        case "bb":
            return "a#"
        case "eb":
            return "d#"
        case _:
            return lowercase


def main() -> None:
    row = random_tone_row()
    print(row)
    reformatted = [reformat_to_sharps(p) for p in row]
    print(reformatted)
    abjad.show(abjad.illustrate(row))

def make():
    row = random_tone_row()
    # start with empty lists
    notes, durations = [[], []]

    # iterate over the row, getting index and PitchClass
    for i, pc in enumerate(row):
        d_this : int = pc.number()
        d_next : int = row.items[(i + 1) % 12].number()
        # this is a hack. confirm with the babbit paper
        if d_next == 0:
            d_next += 1 
        # if we are on the first index, and we don't have a duration of 0, 
        # insert a rest of that duration instesd
        if (i == 0) and (d_this != 0):
            notes.extend([[]])
            durations.extend([abjad.Duration(d_this, 16)])
        notes.extend([abjad.NamedPitch(pc)])
        durations.extend([abjad.Duration(d_next, 16)])

    # build out the staff structures from the note and duration lists
    pitch_list = abjad.makers.make_pitch_lists(notes)
    leaves = abjad.makers.make_leaves(
        pitch_list, durations
    )
    # voice = abjad.Voice([staff], name="Piezo")

    # check the duration, and figure out how many rests to add for it to be correct)
    print(abjad.get.duration(leaves))
    duration = abjad.get.duration(leaves).as_fraction()
    final_rest, _ = abjad.duration.pair_with_denominator(duration, 16)
    final_rest = 12 - final_rest % 12
    print(final_rest)
    
    if final_rest != 0:
        leaves += abjad.makers.make_leaves([[]], [abjad.Duration(final_rest, 16)])
    

    print(abjad.get.duration(leaves))
    staff = abjad.Staff(leaves)
    abjad.attach(abjad.TimeSignature((3, 4)), abjad.get.leaf(staff, 0), context=None)
    staff.remove_commands().append("Note_head_engraver")
    staff.consists_commands().append("Completion_head_engraver")
    staff.remove_commands().append("Rest_engraver")
    staff.consists_commands().append("Completion_rest_engraver")
    score = abjad.Score([staff], name="flagday")
    abjad.show(score)

if __name__ == "__main__":
    make() 
