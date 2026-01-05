![paisley logo](assets/paisley-1bit-firmware.png)

# flagday

off the grid, decentralized cruising. prepared for [**sweeThe4rTs**](https://seattlepride.org/events/sweethearts-a-t4t-art-show), opening February 13, 2026, at Common Objects, Seattle, WA.

## firmware setup

flagday's `firmware` directory is a Git submodule to [anarchivist/meshtastic-firmware](https://github.com/anarchivist/meshtastic/firmware), a light fork of the official Meshtastic firmware distro.

1. prereqs: Git, PlatformIO, and maybe VSCode.
2. clone this repo
3. `git submodule update --init --recursive`

because of how PlatformIO works, you'll need to open up the `firmware` directory in its own VSCode window. annoying, i know. beyond that, you can more or less just consult the [Building Meshtastic Firmware](https://meshtastic.org/docs/development/firmware/build/) page in the official docs.