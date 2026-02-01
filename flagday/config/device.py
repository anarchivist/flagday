"""
Device configuration management tooling.
"""

import argparse
import copy
import os

from typing import Any, Iterable

import yaml

from rtttl import parse_rtttl

DEFAULT_BASE_CONFIG: str = os.path.join(os.getcwd(), "config", "base.yaml")
DEVICE_CONFIG_MAX_LENGTH: dict[str, int] = {
    "owner": 40, "owner_short": 5, "ringtone": 230
}
INVALID_BASE_KEYS: Iterable[str] = DEVICE_CONFIG_MAX_LENGTH.keys()
INVALID_BASE_SECURITY_KEYS: Iterable[str] = ["privateKey", "publicKey"]
parser = argparse.ArgumentParser(
    prog="flagday.config.device",
    description="builds flagday device configs"
)
parser.add_argument("-c", "--config", default=DEFAULT_BASE_CONFIG)
parser.add_argument("-o", "--owner", type=str)
parser.add_argument("-s", "--owner-short", type=str)
parser.add_argument("-r", "--ringtone", type=str)
parser.add_argument("-f", "--output-file")


class InvalidDeviceConfiguration(Exception):
    """
    A catch-all exception for flagday-
    """
    pass


def load_base_config(filename: str = DEFAULT_BASE_CONFIG) -> dict[str, Any]:
    with open(filename, encoding="utf8") as file:
        base_config = yaml.safe_load(file)
    return base_config


def validate_base_config(cfg: dict[str, Any]) -> bool:
    """
    Gently validate a flagday Meshtastic device base config. In this case
    we are treating only the presence of INVALID_BASE_KEYS at the top level
    and INVALID_BASE_SECURITY_KEYS under the `security` key as invalid.

    :param cfg: a parsed device configuration
    :type cfg: dict[str, Any]
    :return: whether the configuration is valid
    :rtype: bool
    """
    rv = None
    security_keys = cfg.get("security")
    if any(k in INVALID_BASE_KEYS for k in cfg):
        rv = False
        raise InvalidDeviceConfiguration(
            "owner, owner_short, or ringtone not valid for base configs"
        )
    elif security_keys and any(
        k in INVALID_BASE_SECURITY_KEYS for k in security_keys
    ):
        rv = False
        raise InvalidDeviceConfiguration(
            "security.privateKey/security.publicKey not valid for base configs"
        )
    else:
        rv = True
    return rv


def generate_device_config(
    base_config: dict[str, Any],
    owner: str,
    owner_short: str,
    ringtone: str
) -> dict[str, Any]:
    """
    Generate a device configuration from a base config and other args.

    :param base_config: a parsed base configuration
    :type base_config: dict[str, Any]
    :param owner: Meshtastic device owner name
    :type owner: str
    :param owner_short: Meshtastic device owner shortname
    :type owner_short: str
    :param ringtone: Unparsed RTTTL ringtone string
    :type ringtone: str
    :return: The merged device configuration
    :rtype: dict[str, Any]
    :raises: InvalidDeviceConfiguration, rtttl.InvalidDefaultsError,
             rtttl.InvalidElementError, rtttl.InvalidNoteError,
             rtttl.InvalidRTTTLFormatError
    """
    device_config = copy.deepcopy(base_config)
    validate_base_config(device_config)
    for prop, max_length in DEVICE_CONFIG_MAX_LENGTH.items():
        value = locals()[prop]
        if len(value.encode("utf-8")) > max_length:
            raise InvalidDeviceConfiguration(
                f"{prop} \"{value}\" is > {max_length} bytes"
            )
        elif prop == "ringtone":
            # rtttl will raise exceptions if it's invalid
            try:
                _ = parse_rtttl(ringtone, strict_note_syntax=True)
            except Exception:
                raise

        device_config[prop] = value

    return device_config


if __name__ == "__main__":
    args = parser.parse_args()
    base_config = load_base_config(args.config)
    device_config = generate_device_config(
        base_config,
        owner=args.owner,
        owner_short=args.owner_short,
        ringtone=args.ringtone
    )
    if args.output_file is not None:
        with open(args.output_file, 'w') as of:
            yaml.dump(device_config, of)
    else:
        print(yaml.dump(device_config))
