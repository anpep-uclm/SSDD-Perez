#!/usr/bin/env python
'''
IceGauntlet distribution script
'''

import sys
import glob
from os.path import expanduser, join
from setuptools import setup, find_packages

__version__ = '0.0.1'
__author__ = 'Tobias Diaz'
__email__ = 'tobias.diaz@uclm.es'
__license__ = 'GPLv3'


assets_destination = 'icegauntlet/assets'
if '--user' in sys.argv:
    # Installation on HOME folder
    assets_destination = expanduser('~') + '/.{}'.format(assets_destination)
elif 'install' in sys.argv:
    # Installation on /usr/local
    assets_destination = join(sys.prefix, 'local/share', assets_destination)
else:
    # Installation on /usr (used for packaging)
    assets_destination = join(sys.prefix, 'share', assets_destination)


setup(
    name='icegauntlet',
    version=__version__,
    description='Gauntlet online',
    author=__author__,
    author_email=__email__,
    license=__license__,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GPLv3 License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Intended Audience :: Education',
        'Intended Audience :: Developers',
        'Topic :: Games/Entertainment',
        'Topic :: Games/Entertainment :: Multi-User Dungeons (MUD)'
    ],
    keywords='gaming development',
    packages=find_packages('./'),
    scripts=['dungeon_local'],
    data_files=[(assets_destination, glob.glob('assets/*'))],
    include_package_data=True,
    zip_safe=False
)
