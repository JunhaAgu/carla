import glob
import os
import sys

import carla

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

def main():
    try:
        client = carla.Client("localhost", 2000)
        client.set_timeout(10)
        world = client.load_world('Town01')
        map = world.get_map()
        waypoints = map.generate_waypoints(1.0)
        for w in waypoints:
            world.debug.draw_string(w.transform.location, 'O', draw_shadow=False,
                                       color=carla.Color(r=255, g=0, b=0), life_time=120.0,
                                       persistent_lines=True)
        

    finally:
        print('delete actorList')

if __name__ == '__main__':
    main()