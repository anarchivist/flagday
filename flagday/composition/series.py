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
    timepoint_set: List[abjad.Duration] = []

    if not isinstance(series, abjad.PitchClassSegment):
        series = abjad.PitchClassSegment(series)

    for i, current_tp in enumerate(series):
        next_tp: int = series.items[(i + 1) % len(series.items)].number()
        interval = (next_tp - current_tp.number()) % len(series.items)

        # Interval 0 represents a full cycle of series length, not duration 0.
        # Negative intervals should be offset by the length of the series.
        if interval <= 0:
            interval += len(series.items)

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
