import re
from typing import List

import abjad

from flagday.composition.series import (
    SeriesSeq,
    generate_babbitt_timepoint_set,
    generate_pitch_octave_series,
    generate_random_series,
)

type LeafCollection = List[abjad.Note | abjad.Tuplet]

PREAMBLE: str = r"""#(set-global-staff-size 20)
date = #(strftime "%Y-%m-%d" (localtime (current-time)))
\header {
    composer = \markup {
        \override #'(font-name . "DINish Bold") "María Dolores A. Matienzo"
    }
    title = \markup { \override #'(font-name . "DINish Bold") "flagday" }
    instrument = \markup {
        \override #'(font-name . "DINish Regular")
        \column {
            \center-align {
                \smaller {
                    \override #'(font-name . "DINish SemiBold Italic")
                    \line \italic { "for 4 or more piezoelectric buzzers" }
                }
                \vspace #0.5
                \line {
                    \override #'(font-name . "DINish SemiBold")
                    \small  "(5'00\" ~ 20'00\")"}
                \vspace #0.5
                \line {
                        \override #'(font-name . "DINish Regular Italic")
                        \normal-text \smaller \italic
                        "Piezoelectric buzzers should sound at irregular intervals during the piece's duration as if they were ringtones."
                }
                \vspace #2
            }
        }
    }
    tagline = ##f
    copyright = \markup {
        \override #'(font-name . "DINish Bold")
        \smallCaps "© & ℗ 2026 Imprecision Art (ASCAP)"
    }
}
\layout {
    \context {
        \Staff
        \override VerticalAxisGroup.staff-staff-spacing.minimum-distance = #22
    }
    \context {
        \Score
        \override SystemStartBar.stencil = ##f
    }
}
\paper {
    page-count = 1
    system-system-spacing.stretchability = #15
}
"""


def make_series_notes(series: SeriesSeq) -> LeafCollection:
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
        series: abjad.PitchClassSegment, offset: int = 0, factor: int = 2
) -> abjad.Staff:
    """
    iteratively create staves and voices, with instrument name annotation

    :param series: input series, e.g. a tone row
    :type series: abjad.PitchClassSegment
    :param offset: start index, e.g. for an iterator based on range()
    :type offset: int
    :param factor: multiplication factor for series rotatio
    :type factor: int
    :return: the combined staff
    :rtype: abjad.Staff
    """
    current_series = series.rotate(offset * factor)
    voice = abjad.Voice(name=f"Voice_{offset}")
    notes = make_series_notes(current_series)
    print(rtttl_from_notes(notes[:]))
    voice.extend(notes)
    staff = abjad.Staff([voice], name=f"Staff_{offset}")
    string = r"""
    \markup \smaller {
        \hspace #-0.75 \override #'(font-name . "DINish Regular") "Piezo"""
    string += f" {offset + 1}\" " + "\n}"
    instrument_name = abjad.InstrumentName(string)
    abjad.attach(instrument_name, notes[0])
    return staff

def rtttl_from_notes(notes: List[abjad.Note | abjad.Tuplet]) -> str:
    abjad.iterpitches.respell_with_sharps(notes[:])
    rtttl = []
    for c in abjad.iterate.components(notes):
        if isinstance(c, abjad.Note):
            dot = ''
            pitch = c.written_pitch().get_name_in_locale('us').lower() # type: ignore
            duration = c.written_duration().lilypond_duration_string()
            d = re.findall(r"\d+", duration)
            if '.' in duration:
                rtttl.append(f"{d[0]}{pitch}.")
                if '..' in duration:
                    rtttl.append(f"{int(d[0])*2}{pitch}")
            else:
                rtttl.append(f"{d[0]}{pitch}")

    return 'd=16,o=5,b=150:' + ','.join(rtttl)

def make_score_from_series(series: SeriesSeq) -> abjad.Score:
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
    score.extend([make_staff_and_voice(series, i, 2) for i in range(6)])
    first_note = abjad.select.note(score, 0)  # pyright: ignore[reportAttributeAccessIssue] # noqa: E501
    abjad.attach(abjad.TimeSignature((3, 4)), first_note)
    abjad.attach(abjad.MetronomeMark(abjad.Duration(1, 4), 150), first_note)

    # rewrite the meter so we don't get double-dotted quarter notes :(
    meter = abjad.Meter(abjad.meter.make_best_guess_rtc((3, 4)))
    meter.rewrite(score[:], maximum_dot_count=1)

    # add a final repeat barline
    abjad.attach(
        abjad.BarLine(":|."),
        abjad.select.note(score, -1)  # pyright: ignore[reportAttributeAccessIssue] # noqa: E501
    )
    return score


def prepare_lilypond_file(
    series: SeriesSeq = generate_random_series(),
) -> abjad.LilyPondFile:
    # leaves = make_series_leaves(series)
    # score = make_score_from_leaves(leaves)
    score = make_score_from_series(series)
    # staff.remove_commands().append("Note_head_engraver")
    # staff.consists_commands().append("Completion_head_engraver")
    # staff.remove_commands().append("Rest_engraver")
    # staff.consists_commands().append("Completion_rest_engraver")

    midi_block = abjad.Block("midi")
    layout_block = abjad.Block("layout")
    score_block = abjad.Block("score", [score, midi_block, layout_block])
    lilypond_file = abjad.LilyPondFile([PREAMBLE, score_block])
    return lilypond_file


if __name__ == "__main__":
    ly = prepare_lilypond_file()
    # print(ly)
    # abjad.persist.as_pdf(ly, "flagday.pdf")
    # abjad.persist.as_pdf(ly, "flagday.midi")
    abjad.show(ly)
