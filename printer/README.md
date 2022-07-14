# Printer Configuration References
List of some hardware and software references for printer configuration.

## BTT Octopus

- Board Manual: https://github.com/bigtreetech/BIGTREETECH-OCTOPUS-V1.0/blob/master/BIGTREETECH_Octopus_EN_updated_0719.pdf
- Board Pinout: https://github.com/bigtreetech/BIGTREETECH-OCTOPUS-V1.0/blob/master/Hardware/BIGTREETECH%20Octopus%20-%20PIN.pdf
- Voron Wiring Guide: https://docs.vorondesign.com/build/electrical/v2_octopus_wiring.html

![BTT Octopus Wiring](https://docs.vorondesign.com/build/electrical/images/v2_octopus_wiring.png)

## Voron Documentation
- Website: https://docs.vorondesign.com/
- GitHub: https://github.com/VoronDesign/Voron-Documentation
- V2.4 Assembly Guide: https://github.com/VoronDesign/Voron-2/raw/Voron2.4/Manual/Assembly_Manual_2.4r2.pdf

## Klipper
- Junja2 Template Documentation: https://jinja.palletsprojects.com/en/2.10.x/templates/#
- Klipper G-Code commands: https://www.klipper3d.org/G-Codes.html
- Klipper Command Templates: https://www.klipper3d.org/Command_Templates.html

### Flashing MCU Firmware
For the initial flashing of the Klipper firmware, follow the Voron Documentation. Once Klipper firmware has been
installed, flashing new versions of the firmware can be done by using the following procedure:

1. Stop klipper: `sudo service klipper stop`
2. Navigate to the klipper directory: `cd klipper`
3. Configure the firmware: `make menuconfig`. For instructions on hose to correctly configure settings, follow the
Voron documentation.
4. Compile and flash firmware: `make flash FLASH_DEVICE=<YourSerialFromTheConfigFiles>`
5. Start klipper: `sudo service klipper start`

## Tuning Guides
- https://github.com/AndrewEllis93/Print-Tuning-Guide

## Slicer Settings and Profiles
- Andrew Ellis PIF Profile: https://github.com/AndrewEllis93/Ellis-PIF-Profile
- Doc's PrusaSlicer Profile: https://discord.com/channels/460117602945990666/461133450636951552/670982868054310932

## Adaptive Bedmesh
Adaptive bedmesh is a set of macros and a custom tool that will parse the GCode being printed in order to get
the bed area being used by the print and adjust the printer's bed mesh calibration accordingly. The goal is to
speed up the printing time by only generating a mesh for the area the print will use.

### Requirements
The custom tool requires a version of Moonraker that supports object exclusion. That support was added by commit
6bd46a443385e35d9f27fdf47581b2fa17f15a7b ("metadata: add support for object postprocessing").

### Installation
1. Copy [/printer/klipper/tools/adaptive_bedmesh.py](/printer/klipper/tools/adaptive_bedmesh.py) script to `/home/pi/tools`. The directory will have to be created first.
2. Copy [/printer/config/macros/adaptive_bedmesh.cfg](/printer/config/macros/adaptive_bedmesh.cfg) to `/home/pi/klipper_config`.
3. Add `[include adaptive_bedmesh.cfg]` to `printer.cfg`.
4. In your `PRINT_START` macro call `ADAPTIVE_BEDMESH` instead of `BED_MESH_CALIBRATE`.