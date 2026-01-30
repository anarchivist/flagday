"""
Test device configuration methods.
"""

import unittest

import yaml

from flagday.config import device


class TestDeviceConfiguration(unittest.TestCase):
    def setUp(self) -> None:
        with open('example_base_good.yaml', encoding="utf8") as file:
            self.base_good = yaml.safe_load(file)
        with open('example_base_bad_owner.yaml', encoding="utf8") as file:
            self.base_bad_owner = yaml.safe_load(file)
        with open('example_base_bad_owner_short.yaml', encoding="utf8") as file:
            self.base_bad_owner_short = yaml.safe_load(file)
        with open('example_base_bad_ringtone.yaml', encoding="utf8") as file:
            self.base_bad_ringtone = yaml.safe_load(file)
        self.ringtone_good = \
            "beethoven:o=5,d=4,b=160:c,e,c,g,c,c6,8b,8a,8g,8a,8g,8f,8e,8f,8e,8d,c,e,g,e,c6,g."

