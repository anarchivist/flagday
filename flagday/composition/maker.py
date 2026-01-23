from typing import List

import abjad

from flagday.composition.series import \
    SeriesSeq, generate_babbitt_timepoint_set, generate_pitch_series, \
    generate_random_series

type LeafCollection = List[abjad.Leaf | abjad.Tuplet]

PREAMBLE : str = r"""
date = #(strftime "%Y-%m-%d" (localtime (current-time)))
\header {
    composer = \markup { María Dolores A. Matienzo }
    title = \markup { flagday }
    subtitle = \date
    instrument = \markup { for 4 or more piezoelectric buzzers }
    tagline = ##f
    copyright = \markup { \smallCaps "© & ℗ 2026 Imprecision Art (ASCAP)" }
}"""

def make_series_leaves(series: SeriesSeq) -> LeafCollection:
    if not isinstance(series, abjad.PitchClassSegment):
        series = abjad.PitchClassSegment(series)

    pitch_series = generate_pitch_series(series)
    pitch_list = abjad.makers.make_pitch_lists(pitch_series)
    durations = generate_babbitt_timepoint_set(series)
    leaves = abjad.makers.make_leaves(
        pitch_list,
        durations,
        increase_monotonic=True,
        forbidden_note_duration=abjad.Duration(1, 2),
        forbidden_rest_duration=abjad.Duration(1, 2),
    )
    lists = abjad.mutate.split(leaves, [abjad.Duration(3, 4)], cyclic=True)
    for c in lists:
        abjad.mutate.wrap(c, abjad.Container())
    return leaves


def make_score_from_leaves(leaves: LeafCollection) -> abjad.Score:
    abjad.attach(
        abjad.TimeSignature((3, 4)),
        abjad.get.leaf(leaves, 0)  # type: ignore
    )
    score = abjad.illustrators.make_piano_score(leaves)
    meter = abjad.Meter(abjad.meter.make_best_guess_rtc((3, 4)))
    meter.rewrite(score[:], maximum_dot_count=1)
    abjad.attach(
        abjad.BarLine("|."),
        abjad.select.note(score, -1) # pyright: ignore[reportAttributeAccessIssue]
    )
    return score


# def make_score_from_staff(staff: abjad.Staff) -> abjad.Score:

#     return abjad.Score([staff], name="flagday")


def engrave(series: SeriesSeq = generate_random_series()) -> None:
    leaves = make_series_leaves(series)
    score = make_score_from_leaves(leaves)
    # staff.remove_commands().append("Note_head_engraver")
    # staff.consists_commands().append("Completion_head_engraver")
    # staff.remove_commands().append("Rest_engraver")
    # staff.consists_commands().append("Completion_rest_engraver")
    lilypond_file = abjad.LilyPondFile([PREAMBLE, score])
    abjad.show(lilypond_file)


if __name__ == "__main__":
    engrave()
