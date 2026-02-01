"""
Composition configuration management tooling.
"""

import os
import warnings

import yaml

from rtttl.parser import parse_bpm

from flagday.composition.series import SeriesSeq, generate_random_series

DEFAULT_BPM: int = 160
DEFAULT_COMPOSITION_CONFIG_FILE: str = os.path.join(
    os.getcwd(), "config", "composition.yaml"
)


class CompositionConfig:
    bpm: int = DEFAULT_BPM
    series: SeriesSeq = []

    def __init__(self, bpm: int = DEFAULT_BPM, series: SeriesSeq = []) -> None:
        self.bpm = bpm
        self.series = series

    @classmethod
    def load_from_file(
        cls, filename: str = DEFAULT_COMPOSITION_CONFIG_FILE
    ) -> CompositionConfig:
        with open(filename, encoding="utf8") as file:
            cfg = yaml.safe_load(file)
            if None in (cfg.get("bpm"), parse_bpm(cfg.get("bpm"))):
                warnings.warn(
                    f"bpm {cfg.get["bpm"]} empty or not valid in RTTTL spec",
                    InvalidBPMForRTTTL
                )
                if parse_bpm(cfg.get("bpm")) is None:
                    cfg["bpm"] = DEFAULT_BPM
            if cfg.get("series") is None:
                warnings.warn("series is empty; defaulting to random series")
                cfg["series"] = generate_random_series()

        return CompositionConfig(bpm=cfg["bpm"], series=cfg["series"])


class InvalidBPMForRTTTL(RuntimeWarning):
    pass
