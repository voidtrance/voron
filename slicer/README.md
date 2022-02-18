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