"""
Test series generation methods.
"""

import unittest
import abjad

from flagday.composition import series


class TestSeriesGeneration(unittest.TestCase):
    def setUp(self) -> None:
        self.test_series = [1, 11, 2, 10, 3, 9, 4, 8, 5, 7, 6, 0]
        self.expected_pitch_series = [
            abjad.NamedPitch("cs'"),
            abjad.NamedPitch("b'"),
            abjad.NamedPitch("d'"),
            abjad.NamedPitch("bf'"),
            abjad.NamedPitch("ef'"),
            abjad.NamedPitch("a'"),
            abjad.NamedPitch("e'"),
            abjad.NamedPitch("af'"),
            abjad.NamedPitch("f'"),
            abjad.NamedPitch("g'"),
            abjad.NamedPitch("fs'"),
            abjad.NamedPitch("c'"),
        ]
        self.expected_timepoint_set = [
            abjad.Duration(10, 16),
            abjad.Duration(3, 16),
            abjad.Duration(8, 16),
            abjad.Duration(5, 16),
            abjad.Duration(6, 16),
            abjad.Duration(7, 16),
            abjad.Duration(4, 16),
            abjad.Duration(9, 16),
            abjad.Duration(2, 16),
            abjad.Duration(11, 16),
            abjad.Duration(6, 16),
            abjad.Duration(1, 16),
        ]

    def test_babbitt_timepoint_set_from_list(self) -> None:
        self.assertEqual(
            series.generate_babbitt_timepoint_set(self.test_series),
            self.expected_timepoint_set,
        )

    def test_babbit_timepoint_set_from_tone_row(self) -> None:
        self.assertEqual(
            series.generate_babbitt_timepoint_set(
                abjad.TwelveToneRow(self.test_series)
            ),
            self.expected_timepoint_set,
        )

    def test_generate_random_series(self) -> None:
        self.assertEqual(
            set(series.BASE_SERIES),
            set(series.generate_random_series())
        )
        self.assertCountEqual(
            series.generate_random_series(),
            series.BASE_SERIES
        )

    def test_gen(self) -> None:
        self.assertEqual(
            series.generate_pitch_series(self.test_series),
            self.expected_pitch_series
        )
