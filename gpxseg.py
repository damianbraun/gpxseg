#! /usr/bin/env python
"""gpxseg

Usage:
    gpxseg -c -s <source_folder> -t <target_folder>
    gpxseg -m -s <source_folder> -t <target_folder>

Options:
    -h --help       Show this screen.
    --version       Show version.
    -c              Copy mode.
    -m              Move mode.
    -s --source     Set source folder.
    -t --target     Set target folder.
"""
from __future__ import print_function
from docopt import docopt
args = docopt(__doc__)

from xml.dom import minidom
import datetime
import logging
import os
import shutil
import sys

from nominatim import NominatimReverse

logger = logging.getLogger()
watchpaths = []
watchpaths.append(args['<source_folder>'])
targetpath = args['<target_folder>']


def find_files_in_folder(folderpaths=watchpaths,
                         extentions=['gpx']):
    """
    Return list of paths to files with extentions from second argument which
    are stored in folders from first argument.
    Both arguments should be lists.
    """
    for x in folderpaths:
        x = os.path.expanduser(x)
        for root, dirs, files in os.walk(x):
            for file in files:
                for extention in extentions:
                    if extention in file[-len(extention):]:
                        """
                        file[-len(extention):] beacouse it shuld work only if
                        end of file name is matching, TODO: i can try using
                        endswith method of str
                        """
                        yield os.path.join(root, file)


class Coordinate(object):
    """docstring for Coordinate"""
    def __init__(self, lat, lon, dt):
        self.lat, self.lon = lat, lon
        self.dt = dt
        self.address = ''

    def __repr__(self):
        if self.address:
            return '''Coordinate instance:\nlat: %s\nlon: %s\ndt: %s
address:%s''' % (self.lat, self.lon, self.dt, self.address)
        else:
            return ''''Coordinate instance:\nlat: %s\nlon: %s
dt: %s''' % (self.lat, self.lon, self.dt)

    def fetchaddress(self):
        """docstring for fetchaddress"""

        nomrev = NominatimReverse()
        self.osm = nomrev.query(self.lat, self.lon)

        adr = self.osm['address']

        if 'road' not in adr:
            adr[u'road'] = u''
        if 'path' not in adr:
            adr[u'path'] = u''

        if 'house_number' not in adr:
            adr[u'house_number'] = u''

        if 'city_district' not in adr:
            adr[u'city_district'] = u''
        if 'suburb' not in adr:
            adr[u'suburb'] = u''

        if 'city' not in adr:
            adr[u'city'] = u''
        if 'town' not in adr:
            adr[u'town'] = u''
        if 'village' not in adr:
            adr[u'village'] = u''

        if adr['house_number'] and adr['road']:
            adr[u'road_house_number'] = adr['road'] + u' ' + adr['house_number'] + u', '
        elif adr['road']:
            adr[u'road_house_number'] = adr['road'] + u', '
        elif adr['path']:
            adr[u'road_house_number'] = adr['path'] + u', '
        else:
            adr[u'road_house_number'] = u''

        if adr['city_district'] and adr['suburb']:
            adr[u'district_suburb'] = adr['suburb'] + u', '
        elif adr['city_district']:
            adr[u'district_suburb'] = adr['city_district'] + u', '
        elif adr['suburb']:
            adr[u'district_suburb'] = adr['suburb'] + u', '
        else:
            adr[u'district_suburb'] = u''

        sn = u'{road_house_number}{district_suburb}{city}{town}{village}'.format(**adr)
        self.shortaddress = sn.strip()


class Gpx(object):
    """docstring for Gpx"""
    def __init__(self, filepath):
        self.filepath = str(filepath)

    def load(self):
        """docstring for load"""
        self.DOMTree = minidom.parse(self.filepath)
        trkptlist = self.DOMTree.getElementsByTagName('trkpt')
        self.ITEMS = []
        for item in trkptlist:
            if sys.version_info.major == 3:
                time = str(item.getElementsByTagName('time')[0].firstChild.data.encode('utf-8'), encoding='utf-8')
            else:
                time = str(item.getElementsByTagName('time')[0].firstChild.data.encode('utf-8'))
            try:
                dt = datetime.datetime.strptime(time, '%Y-%m-%dT%H:%M:%S.%fZ')
            except:
                dt = datetime.datetime.strptime(time, '%Y-%m-%dT%H:%M:%SZ')
            coordinate = Coordinate(item.attributes['lat'].value,
                                    item.attributes['lon'].value,
                                    dt)
            self.ITEMS.append(coordinate)

    def namegen(self):
        """docstring for namegen"""
        def z(x):
            if type(x) == 'str':
                if int(x) < 10:
                    return '0' + x
                else:
                    return x
            else:
                if x < 10:
                    return '0' + str(x)
                else:
                    return str(x)
        first = self.ITEMS[0]
        first.fetchaddress()
        self.newname = '%s-%s-%s %s.%s %s' % (first.dt.year,
            z(first.dt.month), z(first.dt.day), z(first.dt.hour),
            z(first.dt.minute), first.shortaddress
        )
        self.newname = self.newname.replace('/', '.')

    def copyfile(self):
        """docstring for copyfile"""
        target = os.path.join(os.path.expanduser(targetpath), self.newname + '.gpx')
        if sys.version_info.major == 2:
            target = target.encode('utf-8', 'ignore')
        if self.newname:
            shutil.copyfile(self.filepath, target)
            print('%s\ncopied to\n%s' % (self.filepath, target))

    def movefile(self):
        """docstring for movefile"""
        target = os.path.join(os.path.expanduser(targetpath), self.newname + '.gpx')
        if sys.version_info.major == 2:
            target = target.encode('utf-8', 'ignore')
        if self.newname:
            shutil.move(self.filepath, target)
            print('%s\nmoved to\n%s' % (self.filepath, target))


def main():
    for f in find_files_in_folder():
        gpx = Gpx(f)
        gpx.load()
        gpx.namegen()
        if args['-c']:
            gpx.copyfile()
        if args['-m']:
            gpx.movefile()
        print('')

if __name__ == '__main__':
    main()
