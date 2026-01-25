"""
flagday.composition.series : for operations on tone rows, time point sets, etc.
"""

from random import sample
from typing import List, Sequence

import abjad

type SeriesSeq = Sequence[int] | abjad.PitchClassSegment
BASE_SERIES: List = list(range(12))


def generate_random_series() -> Sequence[int]:
    """
    Convenience method to return a randomized row where len(row) == 12.
    Then you can just:

        tone_row = abjad.TwelveToneRow(items=generate_random_row())
    """
    return sample(BASE_SERIES, len(BASE_SERIES))


def generate_babbitt_timepoint_set(
    series: SeriesSeq, denominator: int = 16
) -> List[abjad.Duration]:
    """
    Generate a time-point set à la Milton Babbitt using the method described by
    Bemman and Meredith (2018). Based on Fabio De Sanctis De Benedictis'
    `FDSDB_XXth_CT` PWGL module.

    @see https://github.com/JulienVincenot/PWGL-community-library/tree/main/User-library/FDSDB_XXth_CT # noqa: E501
    """
    if not isinstance(series, abjad.PitchClassSegment):
        series = abjad.PitchClassSegment(series)

    max_interval: int = len(series.items)
    timepoint_set: List[abjad.Duration] = []

    for i, current_tp in enumerate(series):
        next_tp: int = series.items[(i + 1) % max_interval].number()
        interval = (next_tp - current_tp.number()) % max_interval

        # Interval 0 represents a full cycle of series length, not duration 0.
        # Negative intervals should be offset by the length of the series.
        while interval <= 0:
            interval += max_interval

        timepoint_set.append(abjad.Duration(interval, denominator))

    return timepoint_set


def generate_pitch_series(series: SeriesSeq) -> List[abjad.Pitch]:
    """
    Convenience method to generate a pitch series from a series of pitch
    classes. Not smart!
    """

    if not isinstance(series, abjad.PitchClassSegment):
        series = abjad.PitchClassSegment(series)

    return [abjad.NamedPitch(pc) for pc in series.items]


def generate_pitch_octave_series(
        series: SeriesSeq,
        starting_octave: abjad.Octave = abjad.Octave(4),
        min_octave: abjad.Octave = abjad.Octave(4),
        max_octave: abjad.Octave = abjad.Octave(7),
        ) -> List[abjad.Pitch]:
    if not isinstance(series, abjad.PitchClassSegment):
        series = abjad.PitchClassSegment(series)

    po_series = zip(
        generate_pitch_series(series),
        generate_octave_series(series)
    )

    return [abjad.NamedPitch(po) for po in po_series]  # type: ignore


def generate_octave_series(
    series: SeriesSeq,
    starting_octave: abjad.Octave = abjad.Octave(4),
    min_octave: abjad.Octave = abjad.Octave(4),
    max_octave: abjad.Octave = abjad.Octave(7),
) -> List[abjad.Octave]:
    if not isinstance(series, abjad.PitchClassSegment):
        series = abjad.PitchClassSegment(series)

    current_octave: abjad.Octave = starting_octave
    max_interval: int = len(series.items)
    octave_series: List[abjad.Octave] = []

    for i, current_pc in enumerate(series):
        next_pc: int = series.items[(i + 1) % len(series.items)].number()
        if next_pc >= current_pc.number():
            interval = current_pc.number() + next_pc
        else:
            interval = next_pc - current_pc.number()
        if interval >= max_interval:
            if current_octave.number >= max_octave.number:
                current_octave = min_octave
            else:
                current_octave = abjad.Octave(current_octave.number + 1)
        elif interval < 0:
            if current_octave.number <= min_octave.number:
                current_octave = max_octave
            else:
                current_octave = abjad.Octave(current_octave.number - 1)
        else:
            pass
        octave_series.append(current_octave)

    return octave_series
