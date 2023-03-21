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
3. Configure the firmware: `make menuconfig`. For instructions on how to correctly configure settings, follow the
Voron documentation.
4. Compile and flash firmware: `make flash FLASH_DEVICE=<YourSerialFromTheConfigFiles>`
5. Start klipper: `sudo service klipper start`

### Flashing Octopus Bootloader
To reflash the Octopus (STM32F446XX) bootloader, use the following steps:

1. Disconnect all connections to the Octopus, except 24V and USB.
2. Boot Octopus in DFU mode.
3. Download bootloader:
`wget https://raw.githubusercontent.com/bigtreetech/BIGTREETECH-OCTOPUS-V1.0/master/Firmware/DFU%20Update%20bootloader/bootloader/OctoPus-F446-bootloader-32KB.hex`
4. Convert HEX bootloader firmware to binary:
`objcopy --input-target=ihex --output-target=binary OctoPus-F446-bootloader-32KB.hex bootloader.bin`
5. (Optional) Backup old bootloader:
`sudo dfu-util -d ,0483:df11 -R -a 0 -s 0x8000000:32768 -U old-bootloader.bin`
6. Flash new bootloader:
`sudo dfu-util -d ,0483:df11 -R -a 0 -s 0x8000000:leave -D bootloader.bin`

## Tuning Guides
- https://github.com/AndrewEllis93/Print-Tuning-Guide

## Slicer Settings and Profiles
- Andrew Ellis PIF Profile: https://github.com/AndrewEllis93/Ellis-PIF-Profile
- Doc's PrusaSlicer Profile: https://discord.com/channels/460117602945990666/461133450636951552/670982868054310932

## Adaptive Bedmesh
Adaptive bedmesh is a set of macros and a custom tool that will parse the GCode being printed in order to get
the bed area being used by the print and adjust the printer's bed mesh calibration accordingly. The goal is to
speed up the printing time by only generating a mesh for the area the print will use.

There are various other versions of adaptive bed mesh for Klipper. The advantage (in my opinion) of this version
is that, once setup, it places no further requirements in order to use it:

* There is no need to enable object exclusion in Klipper and/or Moonraker.
* There is no need to re-upload the GCode file.
* Since it processes the GCode file when the macro is called, it works retroactively (on previously uploaded
files).

### Requirements
- The custom tool requires a version of Moonraker that supports object exclusion. That support was added by commit
6bd46a443385e35d9f27fdf47581b2fa17f15a7b ("metadata: add support for object postprocessing"). It is not necessary
to enable object exclusion in Moonraker and/or Klipper. Adaptive Bedmesh just uses the GCode parser that is included
in Moonraker for the purposes of object exclusion. 
- Modified version of gcode_shell_command.py from [/printer/klipper/extras](/printer/klipper/extras/).

### Installation
1. Copy [/printer/klipper/tools/adaptive_bed_mesh.py](/printer/klipper/tools/adaptive_bed_mesh.py) script to 
`/home/pi/tools`. The directory will have to be created first.
2. Copy [/printer/config/macros/adaptive_bed_mesh.cfg](/printer/config/macros/adaptive_bed_mesh.cfg) to 
`/home/pi/klipper_config`.
3. Edit `adaptive_bed_mesh.cfg` and replace `--size={user_vars.hw.volume.x},{user_vars.hw.volume.y}` with 
`--size=<your printer size>,<your printer size>`, where `<your printer size>` is either 250, 300, or 350.
4. Add `[include adaptive_bed_mesh.cfg]` to `printer.cfg`.
5. In your `PRINT_START` macro call `ADAPTIVE_BED_MESH_CALIBRATE` instead of `BED_MESH_CALIBRATE`.
