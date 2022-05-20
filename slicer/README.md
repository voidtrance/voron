# Slicer Configuration Data

This directory contains various slicer configuration data -
filament profiles, print settings, etc. 

## Slicer Data Locations
The location data below is for SuperSlicer but it is probably
valid for any Slic3r derivative.

However, it is much better and easier to use the __--datadir__ argument on the
command line to point SuperSlicer to this directory. This way, the files stored
in this repo will always be used. Also, any modifications from within the slicer
will update the repo files, making it easier to keep up-to-date:

```
<path_to_SuperSlicer.exe>\SuperSlicer.exe --datadir "<path_to_repo>\slicer\profiles"
```

### Filament Profiles
Location: %USER%\AppData\Roaming\SuperSlicer\filament

### Print Profiles
Location: %USER%\AppData\Roaming\SuperSlicer\print

### Printer Profiles
Location: %USER%\AppData\Roaming\SuperSlicer\printer

## Printer/Filament Tuning
The [/tuning](/tuning) directory contains some SuperSlicer project files and GCode
files for tuning the printer, print surface, or filament:

<table>
  <tbody>
    <tr><th>File</th><th>Description</th></tr>
    <tr>
      <td valign="top">PA_Calibrate.gcode</td>
      <td>A pre-generated GCode file for tuning Pressure Advance for a filament.
          Before use, the folloeing parameters need to be set:
          <ul>
            <li>BED - Bed temperature for the filament being tuned.</li>
            <li>EXTRUDER - Extruder temperature for the filament being tuned.</li>
            <li>CHAMBER - Chamber temperature for the filament being tuned.</li>
            <li>FILAMENT_ID - Filament ID of the filament being tuned. See "Filament IDs" below.</li>
          </ul>
       </td>
    </tr>
    <tr>
      <td valign="top">FirstLayer.3mf</td>
      <td>A SuperSlicer project for tuning the first layer of a new print surface.</td>
    </tr>
    <tr>
      <td valign="top">ExtrusionMultiplierTest.3mf</td>
      <td>A SuperSliver project for tuning extrusion multiplier for a filament.
          Open the project, set the filament and ensure that:
          <ul>
            <li>The "Extrusion Multiplier" setting is set to 1.</li>
            <li>"Default Fan Speed" is set to 100.</li>
            <li>"Full fan speed as layer" is set to 1.</li>
            <li>"Layer time goal" is set to 0.</li>
          </ul>
      </td>
    </tr>
  </tbody>
</table>

## Filament IDs
Each filament type/brand has been marked with it's own unique ID. Furthermore, the
IDs have the following format:

```
TTTBBBBUU
```

* T - Filament type
* B - Brand identifier
* U - Sub-branch identifier

The following type codes are defined:

| Code | Type |
| :---: | :--- |
| 100 | PLA |
| 200 | ABS |
| 300 | PETG |

### Filament ID Definitions

| Code | Type | Description
| :--- | :---: | :--- |
| 100000100 | PLA | eSun PLA+ |
| 100000200 | PLA | FilamentFusion HTPLA+ |
| 200000100 | ABS | Sparta ABS+ |