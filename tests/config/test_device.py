"""
Test device configuration methods.
"""

import copy
import unittest

from pathlib import Path

import yaml

from flagday.config.device import (
    generate_device_config, validate_base_config, InvalidDeviceConfiguration
)


FIXTURE_PATH: Path = Path(__file__).parent / 'example_base_good.yaml'


class TestDeviceConfiguration(unittest.TestCase):
    def setUp(self) -> None:
        self.owner_good = "girlscout420"
        self.owner_short_good = "g420"
        self.ringtone_good = "smbdeath:d=4,o=5,b=90:32c6,32c6,32c6,8p,16b,16f6,16p,16f6,16f6., 16e6.,16d6,16c6,16p,16e,16p,16c"  # noqa: E501

        with open(FIXTURE_PATH, encoding="utf8") as file:
            self.base_good = yaml.safe_load(file)
            self.device_good = copy.deepcopy(self.base_good)
            self.device_good["owner"] = self.owner_good
            self.device_good["owner_short"] = self.owner_short_good
            self.device_good["ringtone"] = self.ringtone_good

    def test_validate_good_base_config(self) -> None:
        self.assertTrue(validate_base_config(self.base_good))

    def test_validate_bad_base_configs(self) -> None:
        bad_base_configs = {
            "owner": copy.deepcopy(self.base_good),
            "owner_short": copy.deepcopy(self.base_good),
            "ringtone": copy.deepcopy(self.base_good),
            "security": copy.deepcopy(self.base_good)
        }
        bad_base_configs["owner"]["owner"] = self.owner_good
        bad_base_configs["owner_short"]["owner_short"] = self.owner_short_good
        bad_base_configs["ringtone"]["ringtone"] = self.ringtone_good
        bad_base_configs["security"]["security"] = {
            "privateKey": "foo", "publicKey": "bar"
        }
        for _, c in bad_base_configs.items():
            with self.assertRaises(InvalidDeviceConfiguration):
                validate_base_config(c)

    def test_generate_device_config(self) -> None:
        cfg = generate_device_config(
            self.base_good,
            owner=self.owner_good,
            owner_short=self.owner_short_good,
            ringtone=self.ringtone_good
        )
        self.assertEqual(cfg, self.device_good)
        with self.assertRaises(InvalidDeviceConfiguration):
            _ = generate_device_config(
                self.base_good,
                owner="blah"*230,
                owner_short=self.owner_short_good,
                ringtone=self.ringtone_good
            )
        with self.assertRaises(Exception):
            generate_device_config(
                self.base_good,
                owner="blah"*230,
                owner_short=self.owner_short_good,
                ringtone="Invalid:d=4,o=5,b=90:F#6.,8F#.6,f#"
            )
