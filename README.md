gpxseg
======

CLI Tool for auto renaming gpx files

### Install

```
git clone https://github.com/damianbraun/gpxseg.git
python setup.py install
(or)
sudo python setup.py install
```

### Rename

This tool renames all gpx files with this scheme  
**{year}-{month}-{day} {hour}.{minute} {text-address}.gpx**

#### Examples

2014-05-30 15.53 Wejście nr 11, Wyspa Sobieszewska, Gdańsk.gpx  
2014-06-07 06.16 Karwieńska 3, Oliwa, Gdańsk.gpx

### Usage

```
gpxseg -c -s ~/Dropbox/ -t ~/gpxarchive
```
*This  command will copy all .gpx files within ~/Dropbox/ folder recursively into ~/gpxarchive.*
