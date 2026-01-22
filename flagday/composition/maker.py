import abjad

from flagday.composition.series import *

type LeafCollection = List[abjad.Leaf | abjad.Tuplet]

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

def make_staff_from_leaves(leaves: LeafCollection) -> abjad.Score:
    abjad.attach(abjad.TimeSignature((3, 4)), abjad.get.leaf(leaves, 0)) # type: ignore
    staff = abjad.illustrators.make_piano_score(leaves)
    meter = abjad.Meter(abjad.meter.make_best_guess_rtc((3, 4)))
    meter.rewrite(staff[:], maximum_dot_count=1)
    abjad.attach(abjad.BarLine("|."), abjad.select.note(staff, -1))
    return staff


def make_score_from_staff(staff: abjad.Staff) -> abjad.Score:
    # staff.remove_commands().append("Note_head_engraver")
    # staff.consists_commands().append("Completion_head_engraver")
    # staff.remove_commands().append("Rest_engraver")
    # staff.consists_commands().append("Completion_rest_engraver")
    return abjad.Score([staff], name="flagday")

def engrave(series: SeriesSeq = generate_random_series()) -> None:
    leaves = make_series_leaves(series)
    staff = make_staff_from_leaves(leaves)
    # score = make_score_from_staff(staff)
    abjad.show(staff)

if __name__ == "__main__":
    engrave()