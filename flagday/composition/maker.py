import argparse
import copy
import os
import re

from pathlib import Path
from typing import List

import abjad

from flagday.composition.series import (
    SeriesSeq,
    generate_babbitt_timepoint_set,
    generate_pitch_octave_series,
    generate_random_series,
)
from flagday.config.composition import (
    CompositionConfig,
    DEFAULT_BPM,
    DEFAULT_COMPOSITION_CONFIG_FILE
)

INCLUDES_DIR = os.path.join(os.getcwd(), 'stylesheets')
PREAMBLE_FILE = os.path.join(INCLUDES_DIR, 'preamble.ily')
ringtones: List[str] = []
parser = argparse.ArgumentParser(
    prog="flagday.composition.maker",
    description="builds scores, etc. for flagday"
)
parser.add_argument('-c', '--config', default=DEFAULT_COMPOSITION_CONFIG_FILE)
# parser.add_argument(
#     '-o', '--output', type=str, choices=["ly", "midi", "pdf", "rtttl"]
# )

def make_series_notes(series: SeriesSeq) -> List[abjad.Note | abjad.Tuplet]:
    """
    make a list set of abjad.Notes from an input seriese

    :param series: a series, e.g. a tone row
    :type series: SeriesSeq
    :return: a set of notes to be attended to other abjads
    :rtype: LeafCollection
    """
    if not isinstance(series, abjad.PitchClassSegment):
        series = abjad.PitchClassSegment(series)

    pitch_series = generate_pitch_octave_series(
        series, starting_octave=abjad.Octave(5)
    )
    pitch_list = abjad.makers.make_pitches(pitch_series)
    durations = generate_babbitt_timepoint_set(series)
    notes = abjad.makers.make_notes(
        pitch_list, durations, increase_monotonic=True,
    )
    lists = abjad.mutate.split(notes, [abjad.Duration(3, 4)], cyclic=True)
    for c in lists:
        abjad.mutate.wrap(c, abjad.Container())
    return notes


def make_staff_and_voice(
        series: abjad.PitchClassSegment,
        offset: int = 0,
        factor: int = 2,
        bpm: int = DEFAULT_BPM
) -> abjad.Staff:
    """
    iteratively create staves and voices, with instrument name annotation

    :param series: input series, e.g. a tone row
    :type series: abjad.PitchClassSegment
    :param offset: start index, e.g. for an iterator based on range()
    :type offset: int
    :param factor: multiplication factor for series rotation
    :type factor: int
    :return: the combined staff
    :rtype: abjad.Staff
    """
    current_series = series.rotate(offset * factor)
    voice = abjad.Voice(name=f"Voice_{offset}", simultaneous=False)
    notes = make_series_notes(current_series)
    rtttl = rtttl_from_notes(notes, bpm)
    print(f"P{offset + 1}:{rtttl}")
    voice.extend(notes)
    staff = abjad.Staff([voice], name=f"Staff_{offset}", simultaneous=False)
    string = r"""
    \markup \smaller {
        \hspace #-0.75 \override #'(font-name . "DINish Regular") "Piezo"""
    string += f" {offset + 1}\" " + "\n}"
    instrument_name = abjad.InstrumentName(string)
    rtttl_anno = abjad.Markup(
            r"\markup \fontsize #-5 \override #'(font-family . typewriter) "
            r"{ \hspace #-9"
            f"\"P{offset + 1}:{rtttl}\""
            r"}"
    )
    abjad.attach(instrument_name, notes[0])
    abjad.attach(rtttl_anno, notes[0])
    # abjad.attach(abjad.LilyPondLiteral(r"\override Frame #'extender-length = 32"), notes[0])
    # abjad.attach(abjad.LilyPondLiteral(r"\frameStart"), notes[0])
    # abjad.attach(abjad.LilyPondLiteral(r"\frameEnd"), notes[-1])
    return staff


def rtttl_from_notes(
        notes: List[abjad.Note | abjad.Tuplet], bpm: int = DEFAULT_BPM
    ) -> str:
    """
    Generate a RTTTL ringtone string from a list of abjad.Notes

    :param notes: Notes with pitches and durations
    :type notes: List[abjad.Note | abjad.Tuplet]
    :return: the RTTTL string
    :rtype: str
    """
    rnotes = copy.deepcopy(notes)
    abjad.iterpitches.respell_with_sharps(rnotes)
    rtttl = []
    for c in abjad.iterate.components(rnotes):
        if isinstance(c, abjad.Note):
            pitch = c.written_pitch().get_name_in_locale('us').lower()  # type: ignore # noqa: e%01
            duration = c.written_duration().lilypond_duration_string()
            d = re.findall(r"\d+", duration)
            if '.' in duration:
                rtttl.append(f"{d[0]}{pitch}.")
                if '..' in duration:
                    rtttl.append(f"{int(d[0])*4}{pitch}")
            else:
                rtttl.append(f"{d[0]}{pitch}")

    return f'd=16,o=5,b={bpm}:' + ','.join(rtttl)


def make_score_from_series(series: SeriesSeq, bpm: int = DEFAULT_BPM) -> abjad.Score:
    """
    given an input series, make 6 different staves to be combined into a score
    ready for furtgher processing

    :param series: input series, e.g. a tone row
    :type series: SeriesSeq
    :return: the completed score, rebalanced into time signature and meter
    :rtype: Score
    """
    if not isinstance(series, abjad.PitchClassSegment):
        series = abjad.PitchClassSegment(series)

    # construct the score, attaching the indicators
    score = abjad.Score(name="score")
    score.extend([make_staff_and_voice(series, i, 2, bpm) for i in range(6)])
    first_note = abjad.select.note(score, 0)  # pyright: ignore[reportAttributeAccessIssue] # noqa: E501
    abjad.attach(abjad.TimeSignature((3, 4)), first_note)
    abjad.attach(abjad.MetronomeMark(abjad.Duration(1, 4), bpm), first_note)

    # rewrite the meter so we don't get double-dotted quarter notes :(
    meter = abjad.Meter(abjad.meter.make_best_guess_rtc((3, 4)))
    meter.rewrite(score[:], maximum_dot_count=1)

    # add a final repeat barline
    abjad.attach(
        abjad.BarLine(":|."),
        abjad.select.note(score, -1)  # pyright: ignore[reportAttributeAccessIssue] # noqa: E501
    )
    return score


def prepare_lilypond_file(score: abjad.Score) -> abjad.LilyPondFile:
    layout_block = abjad.Block("layout")
    score_block = abjad.Block("score", [score, layout_block])
    lilypond_file = abjad.LilyPondFile(
        [rf'\include "{PREAMBLE_FILE}"', score_block]
    )
    return lilypond_file


if __name__ == "__main__":
    args = parser.parse_args()
    cfg_path = Path(args.config)
    if cfg_path.is_file():
        cfg = CompositionConfig.load_from_file(args.config)
    else:
        cfg = CompositionConfig(
            bpm=DEFAULT_BPM, series=generate_random_series()
        )
    score = make_score_from_series(cfg.series, bpm=cfg.bpm)
    ly = prepare_lilypond_file(score)
    abjad.show(ly)
