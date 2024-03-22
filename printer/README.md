# Printer Configuration References
List of some hardware and software references for printer configuration.

## BTT Octopus

- Board Manual: https://github.com/bigtreetech/BIGTREETECH-OCTOPUS-V1.0/blob/master/BIGTREETECH_Octopus_EN_updated_0719.pdf
- Board Pinout: [docs/BIGTREETECH Octopus - PIN.pdf](docs/BIGTREETECH%20Octopus%20-%20PIN.pdf)
- Voron Wiring Guide: https://docs.vorondesign.com/build/electrical/v2_octopus_wiring.html

![BTT Octopus Wiring](https://docs.vorondesign.com/build/electrical/images/v2_octopus_wiring.png)

## BTT U2C
-  Manual: https://github.com/bigtreetech/U2C/blob/master/BIGTREETECH%20U2C%20V1.0%26V1.1%20User%20Manual.pdf
- Pinout: https://github.com/bigtreetech/U2C/blob/master/Image/pinout.png

## BTT EBB36
- Manual: https://github.com/bigtreetech/EBB/blob/master/EBB%20CAN%20V1.1%20(STM32G0B1)/EBB36%20CAN%20V1.1/BIGTREETECH%20EBB36%20CAN%20V1.1%20User%20Manual.pdf

![EBB36 Pinout](/printer/docs/EBB36%20CAN%20V1.1&V1.2-PIN.png)

### Toolhead Board HW Configuration
| Usage / Hardware | Connector | Pin | Notes |
|-|-|-|-|
| Hotend heater (Rapido)| Hotend 0 | PB13 ||
| Hotend thermistor (Rapido) | MAX31865 Port | PA4 | Two line PT1000 get wired to the middle two pins |
| Hotend fan | FAN1 | PA0 | Fan is 5V so the input voltage will have to come from Endstop header |
| Part cooling fans | FAN2 | PA1 ||
| X endstop | Endstop | PB6 ||
| Klicky Probe | Endstop | PB5 ||
| Filament Sensor | Probe | PB8 ||
| Filament Unload Button | Probe | PB9 ||
| LEDs | RFB | PD3 ||

## Documentation
### Voron Documentation
- Website: https://docs.vorondesign.com/
- GitHub: https://github.com/VoronDesign/Voron-Documentation
- V2.4 Assembly Guide: https://github.com/VoronDesign/Voron-2/raw/Voron2.4/Manual/Assembly_Manual_2.4r2.pdf

### Klipper Documentation
- Junja2 Template Documentation: https://jinja.palletsprojects.com/en/2.10.x/templates/#
- Klipper G-Code commands: https://www.klipper3d.org/G-Codes.html
- Klipper Command Templates: https://www.klipper3d.org/Command_Templates.html

## Board Firmware Guides

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

### Flashing CAN device firmware
* https://canbus.esoterical.online/

## Tuning Guides
- https://ellis3dp.com/Print-Tuning-Guide/
- PA Calibration: https://ellis3dp.com/Pressure_Linear_Advance_Tool/
- EM Calibration: https://ellis3dp.com/Print-Tuning-Guide/articles/extrusion_multiplier.html#method

## Slicer Settings and Profiles
- Andrew Ellis PIF Profile: https://github.com/AndrewEllis93/Ellis-PIF-Profile
- Doc's PrusaSlicer Profile: https://discord.com/channels/460117602945990666/461133450636951552/670982868054310932
