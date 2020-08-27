#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

'''
Shortcut to search for assets files
'''

import os.path


_FOLDERS_PATH_ = [
    'assets',
    '$HOME/.icegauntlet/assets',
    '/usr/local/share/icegauntlet/assets',
    '/usr/share/icegauntlet/assets'
]

def search(filename):
    '''Search for given filename in assets folder and return if found'''
    if os.path.exists(filename):
        return filename

    for candidate in _FOLDERS_PATH_:
        candidate = os.path.join(os.path.expandvars(os.path.expanduser(candidate)), filename)
        if os.path.exists(candidate):
            return candidate

    return None
