#! /usr/bin/env python
"""gpxseg

Usage:
    gpxseg -c
    gpxseg -m
    gpxseg -c <source_folder> <target_folder>
    gpxseg -m <source_folder> <target_folder>
    gpxseg -c -s <source_folder> -t <target_folder>
    gpxseg -m -s <source_folder> -t <target_folder>
    gpxseg settings

Options:
    -h --help       Show this screen.
    --version       Show version.
    -c              Copy mode.
    -m              Move mode.
    -s --source     Set source folder.
    -t --target     Set target folder.
    settings        Create settings file in ~/.gpxseg
"""
from __future__ import print_function
from docopt import docopt
args = docopt(__doc__)

from xml.dom import minidom
from colorama import Fore
import datetime
import logging
import os
import shutil
import sys
import tzlocal
import pytz
import pickle

from nominatim import NominatimReverse

logger = logging.getLogger()
watchpaths = []
watchpaths.append(args['<source_folder>'])


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


class Coordinate():
    """
    Class for storing pair of lat and lon, time and additional info.
    """
    def __init__(self, lat, lon, dt):
        self.lat, self.lon = lat, lon
        self.dt = dt
        utc = pytz.utc
        self.dt = utc.localize(self.dt)
        localtimezone = tzlocal.get_localzone()
        self.dt = self.dt.astimezone(localtimezone)
        self.address = ''

    def __repr__(self):
        if self.address:
            return '''Coordinate instance:\nlat: %s\nlon: %s\ndt: %s
address:%s''' % (self.lat, self.lon, self.dt, self.address)
        else:
            return ''''Coordinate instance:\nlat: %s\nlon: %s
dt: %s''' % (self.lat, self.lon, self.dt)

    def fetchaddress(self):
        """
        Method for fetching address from Nominatim, and formating it in
        shortaddress.
        """
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
            adr[u'road_house_number'] = (adr['road'] + u' '
                                         + adr['house_number'] + u', ')
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


class File():
    """
    Base class for files.
    """
    def __init__(self, filepath):
        self.filepath = os.path.expanduser(filepath)


class Gpx(File):
    """
    Class for whole gpx file.
    """
    def load(self):
        """
        Method for loading all trkpt items from xml to self.ITEMS
        """
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
        """
        Method for generating newname for file.
        """
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
                                              z(first.dt.month),
                                              z(first.dt.day),
                                              z(first.dt.hour),
                                              z(first.dt.minute),
                                              first.shortaddress)
        self.newname = self.newname.replace('/', '.')

    def copyfile(self):
        """
        Method for copying file.
        """
        target = os.path.join(os.path.expanduser(args['<target_folder>']),
                              self.newname + '.gpx')
        if sys.version_info.major == 2:
            target = target.encode('utf-8', 'ignore')
        if self.newname:
            shutil.copyfile(self.filepath, target)
            print('%s\ncopied to\n%s' %
                  (self.filepath.replace(os.environ['HOME'], '~'),
                   target.replace(os.environ['HOME'], '~')))

    def movefile(self):
        """
        Method for moving file.
        """
        target = os.path.join(os.path.expanduser(args['<target_folder>']),
                              self.newname + '.gpx')
        if sys.version_info.major == 2:
            target = target.encode('utf-8', 'ignore')
        if self.newname:
            shutil.move(self.filepath, target)
            print('%s\nmoved to\n%s' %
                  (self.filepath.replace(os.environ['HOME'], '~'),
                   target.replace(os.environ['HOME'], '~')))


class Settings(File):
    """
    Class for managing settings file.
    """
    def load(self):
        file = open(self.filepath, 'rb')
        object = pickle.load(file)
        file.close()
        return object

    def dump(self, object):
        try:
            file = open(self.filepath, 'wb')
            pickle.dump(object, file)
            file.close()
        except IOError:
            file = open(self.filepath, 'w+')
            file.close()
            self.dump(object)

    def create(self):
        source = os.path.expanduser(raw_input('Type in source path:'))
        target = os.path.expanduser(raw_input('Type in target path:'))
        self.dump((source, target))


def main():
    settings = Settings('~/.gpxseg.pkl')
    if args['settings']:
        settings.create()
        sys.exit(1)
    else:
        obj = settings.load()
        args['<source_folder>'], args['<target_folder>'] = obj
    if (not os.path.isdir(args['<source_folder>']) or not os.path.isdir(args['<target_folder>'])):
        print('One of paths is not a folder,\nplease specify folder paths')
        sys.exit(2)
    colors = [Fore.BLUE, Fore.GREEN, Fore.RED, Fore.YELLOW]
    num = 0
    for f in find_files_in_folder([args['<source_folder>']]):
        gpx = Gpx(f)
        gpx.load()
        gpx.namegen()
        print(colors[num])
        if args['-c']:
            gpx.copyfile()
        if args['-m']:
            gpx.movefile()
        if num >= len(colors)-1:
            num = 0
        else:
            num += 1

if __name__ == '__main__':
    main()
