#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

'''
   Handle TMX/TSX files
'''

import math
import os.path

try:
    import xmltodict
except ImportError as error:
    print('ERROR: xmltodict library is required to use this extension')
    raise error


class FileReader:
    '''Base for read data from file'''
    def __init__(self, filename):
        if not os.path.exists(filename):
            raise OSError('File not found: {}'.format(filename))
        self._filename_ = filename

    @property
    def source(self):
        '''Original **full** filename'''
        return os.path.abspath(self._filename_)

    @property
    def filename(self):
        '''Original filename'''
        return os.path.basename(self.source)

    @property
    def path(self):
        '''Full path of file'''
        return os.path.abspath(os.path.dirname(self.source))

    @property
    def data(self):
        '''File contents'''
        raise NotImplementedError()

    @property
    def map_data(self):
        '''File contents'''
        return self.get_field_value('layers')[0]['data']

    @property
    def map_encoding(self):
        '''Contents encoding'''
        return None

    @property
    def map_width(self):
        '''Map width'''
        return self.get_field_value('layers')[0]['width']

    @property
    def map_height(self):
        '''Map height'''
        return self.get_field_value('layers')[0]['height']

    def assert_field_exists(self, field_name):
        '''Check if a given field_name is defined in file'''
        if field_name not in self.data:
            raise KeyError('Key "{}" must be defined in source file'.format(field_name))
            
    def get_field_value(self, field_name):
        '''Get value of a given field_name'''
        self.assert_field_exists(field_name)
        return self.data[field_name]


class XMLFile(FileReader):
    '''Read data from a XML file'''
    def __init__(self, filename):
        super(XMLFile, self).__init__(filename)
        with open(self.source, 'rb') as contents:
            self._data_ = xmltodict.parse(contents, dict_constructor=dict)

    @property
    def data(self):
        return self._data_

    def assert_field_exists(self, field_name):
        if field_name in self.data:
            return
        if '@{}'.format(field_name) in self.data:
            return
        if '#{}'.format(field_name) in self.data:
            return
        raise KeyError('Key "{}" must be defined in source file'.format(field_name))

    def get_field_value(self, field_name):
        self.assert_field_exists(field_name)
        if field_name in self.data:
            return self.data[field_name]
        if '@{}'.format(field_name) in self.data:
            return self.data['@{}'.format(field_name)]
        if '#{}'.format(field_name) in self.data:
            return self.data['#{}'.format(field_name)]
        raise KeyError(field_name)


class TMXFile(XMLFile):
    '''TMX xml file reader'''
    def __init__(self, filename):
        super(TMXFile, self).__init__(filename)
        self._data_ = self.data['map']
        self._properties_ = {}
        properties = self._data_.get('properties', None)
        if properties:
            for prop in properties.values():
                self._properties_[prop['@name']] = prop['@value']

    @property
    def data(self):
        return self._data_

    @property
    def properties(self):
        '''Custom properties of TMX file'''
        return self._properties_

    @property
    def map_data(self):
        '''Map data'''
        return self.get_field_value('layer')['data']['#text']

    @property
    def map_encoding(self):
        return self.get_field_value('layer')['data']['@encoding']

    @property
    def map_width(self):
        return self.get_field_value('layer')['@width']

    @property
    def map_height(self):
        return self.get_field_value('layer')['@height']

    @property
    def tilesets(self):
        '''External tilesets file'''
        try:
            return [self.get_field_value('tileset')['@source']]
        except KeyError:
            return []


class TSXFile(XMLFile):
    '''TSX xml file reader'''
    def __init__(self, filename):
        super(TSXFile, self).__init__(filename)
        self._data_ = self.data['tileset']

    @property
    def data(self):
        return self._data_


class TileMap:
    '''A simple TileMap wrapper'''
    def __init__(self, map_reader):
        self._src_ = map_reader
        if len(self._src_.tilesets) > 1:
            raise ValueError('More than one tilesets per map is not supported!')
        self._tileset_ = TileSet(TSXFile(os.path.join(self._src_.path, self._src_.tilesets[0])))
        if self._tileset_.tile_width != int(self._src_.get_field_value('tilewidth')):
            raise ValueError('Tile width value mistmatch!')
        if self._tileset_.tile_height != int(self._src_.get_field_value('tileheight')):
            raise ValueError('Tile height value mistmatch!')
        self._map_ = _decode_map_(self._src_.map_data, self._src_.map_encoding)
        if len(self._map_) != self.height:
            raise ValueError('Map data and map height mistmach!')
        if len(self._map_[0]) != self.width:
            raise ValueError('Map data and map width mistmach!')

        for x in range(self.width):
            for y in range(self.height):
                tile = self.tile_at(x, y)
                if (tile is not None) and  (tile not in self.tileset):
                    raise ValueError('Tile at ({}, {}) is undefined'.format(x, y))

    @property
    def properties(self):
        '''Custom properties of the map'''
        return self._src_.properties

    @property
    def width(self):
        '''Map width'''
        return int(self._src_.map_width)

    @property
    def height(self):
        '''Map height'''
        return int(self._src_.map_height)

    @property
    def tileset(self):
        '''External tileset object'''
        return self._tileset_

    @property
    def data(self):
        '''Map contents'''
        return self._map_

    def tile_at(self, x, y):
        '''Get tileID of a given position'''
        if x not in range(self.width):
            raise ValueError('x={} is outside of the map'.format(x))
        if y not in range(self.height):
            raise ValueError('y={} is outside of the map'.format(y))
        # Tiled use 0 for unefined, 1 for Tile #0 and so on
        tile = self.data[y][x]
        if tile == 0:
            return None
        return tile - 1

    def __str__(self):
        return '{}x{} map'.format(self.width, self.height)


class TileSet:
    '''A simple TileSet wrapper'''
    def __init__(self, tile_reader):
        self._src_ = tile_reader
        if (self.tile_width % 8) or (self.tile_height % 8):
            raise ValueError('Pyxel only supports tiles with a size of 8x8 or multiple')
        image_width = float(self._src_.get_field_value('image')['@width'])
        image_height = float(self._src_.get_field_value('image')['@height'])
        source_image = os.path.join(self._src_.path, self._src_.get_field_value('image')['@source'])
        needed_images = int(math.ceil(image_width / 256.0) * math.ceil(image_height / 256.0))
        if needed_images > 3:
            raise ValueError('TileSet image is too big. It should be fit in three images of 256x256 each.')
        if not os.path.exists(source_image):
            raise OSError('Referenced image file "{}" not found!'.format(source_image))

    def __len__(self):
        return int(self._src_.get_field_value('tilecount'))

    def __contains__(self, tile_id):
        return tile_id in range(len(self))

    @property
    def tile_width(self):
        '''Width in pixels of a tile'''
        return int(self._src_.get_field_value('tilewidth'))

    @property
    def tile_height(self):
        '''Height in pixels of a tile'''
        return int(self._src_.get_field_value('tileheight'))

    @property
    def tile_size(self):
        '''Size in pixels of a tile'''
        return (self.tile_width, self.tile_height)

    @property
    def name(self):
        '''Name of tileset'''
        return self._src_.get_field_value('name')

    def __str__(self):
        return '{} tileset of {} {}x{} tiles'.format(
            self.name, self.__len__(), self.tile_width, self.tile_height
        )


def _decode_map_(data, encoder):
    '''Decode TileMap stored in a TMX file'''
    if encoder is None:
        return data
    elif encoder.lower() == 'csv':
        return _CSV_decoder_(data)
    else:
        raise ValueError('Unsupported encoding: {}'.format(encoder))


def _CSV_decoder_(map_data):
    decoded_map = []
    for row in map_data.splitlines():
        if row.endswith(','):
            row = row[:-1]
        map_row = []
        for tile_id in row.split(','):
            map_row.append(int(tile_id))
        decoded_map.append(map_row)
    return decoded_map


def load_tilemap(filename):
    '''Factory for read TMX files'''
    return TileMap(TMXFile(filename))
