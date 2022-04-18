import glob
import os
from random import random
import sys
from pathlib import Path
import random

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla
import time
from datetime import date
import agu_generator_KITTI as gen

def mian():
    start_record_full = time.time()