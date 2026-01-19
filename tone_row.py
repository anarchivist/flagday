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
    reformatted = [reformat_to_sharps(p) for p in row]
    print(reformatted)
    # abjad.show(abjad.illustrate(row))


if __name__ == "__main__":
    main()
