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
import numpy as np

# ==============================================================================
# -- Add PythonAPI for release mode --------------------------------------------
# ==============================================================================
try:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/carla')
except IndexError:
    pass
from agents.navigation.behavior_agent import BehaviorAgent
from agents.navigation.basic_agent import BasicAgent

def main():
    start_record_full = time.time()
    
    map_number = 1;
    
    fps_simu = 100.0
    time_stop = 2.0
    nbr_frame = 300 #max = 10000
    nbr_walkers = 50
    nbr_vehicles = 50
    
    actor_list = []
    vehicles_list = []
    all_walkers_id = []
    data_date = date.today().strftime("%Y_%m_%d")
    
    agent_start_point = carla.Transform(carla.Location(x=190.0,y=55.6,z=2), carla.Rotation(pitch = 0, yaw=180, roll=0))
    agent_waypoint = np.array([
     (carla.Location(x=120.0, y=55.5,  z=0.3)), #첫번째 교차로 전 
     (carla.Location(x=88.4,  y=88.3,  z=0.3)), #좌회전 후 
     (carla.Location(x=230.0, y=133.5, z=0.3)), #좌회전 후 
     (carla.Location(x=338.8, y=88.3,  z=0.3)), #긴 직진 후 좌회전
     (carla.Location(x=300.0, y=55.5,  z=0.3)), #마지막 좌회전 후
     (carla.Location(x=120.0, y=55.5,  z=0.3))  #최종 목적지
     ])
    
    init_settings = None
    
    try:
        client = carla.Client('localhost',2000)
        client.set_timeout(2.0) # seconds
        init_settings = carla.WorldSettings()
        
        client.set_timeout(100.0)
        print("Map Town0" + str(map_number))
        world = client.load_world("Town0" + str(map_number))
        folder_output = "../../agu_results/%s/generated" %(world.get_map().name)
        print(folder_output)
        os.makedirs(folder_output) if not [os.path.exists(folder_output)] else [os.remove(f) for f in glob.glob(folder_output+"/*") if os.path.isfile(f)]
        # client.start_recorder(os.path.dirname(os.path.realpath(__file__))+"/"+folder_output+"/recording.log")
        client.start_recorder(os.path.realpath(folder_output)+"/recording.log")
        
        # Weather
        world.set_weather(carla.WeatherParameters.ClearNoon) #WetCloudyNoon
        # ClearNoon, CloudyNoon, WetNoon, WetCloudyNoon, SoftRainNoon, MidRainyNoon, HardRainNoon, 
        # ClearSunset, CloudySunset, WetSunset, WetCloudySunset, SoftRainSunset, MidRainSunset, HardRainSunset.
        
        # Set Synchronous mode
        settings = world.get_settings()
        settings.synchronous_mode = True
        settings.fixed_delta_seconds = 1.0/fps_simu
        settings.no_rendering_mode = False
        world.apply_settings(settings)
        
        # traffic_manager = client.get_trafficmanager()
        # traffic_manager.set_synchronous_mode(True)
        
        # Create KITTI vehicle
        blueprint_library = world.get_blueprint_library()
        bp_KITTI = blueprint_library.filter('vehicle.audi.tt')[0]
        bp_KITTI.set_attribute('color','228,239,241')
        bp_KITTI.set_attribute('role_name','KITTI')
        start_pose = agent_start_point
        KITTI = world.try_spawn_actor(bp_KITTI, start_pose)
        try:
            physics_control = KITTI.get_physics_control()
            physics_control.use_sweep_wheel_collision = True
            KITTI.apply_physics_control(physics_control)
        except Exception:
            pass
        
        actor_list.append(KITTI)
        
        agent = BehaviorAgent(KITTI, behavior = "normal")
        # agent = BasicAgent(KITTI)
        # "cautious", "normal", "aggressive"
        
        print('Created %s' %KITTI)
        
        # Spawn vehicles and walkers
        gen.spawn_npc(client, nbr_vehicles, nbr_walkers, vehicles_list, all_walkers_id)
        print("spawn_npc is generated") #agu
        
        # Wait for KITTI to stop
        start = world.get_snapshot().timestamp.elapsed_seconds
        print("Waiting for KITTI to stop ...")
        while world.get_snapshot().timestamp.elapsed_seconds-start < time_stop: world.tick()
        print("KITTI stopped")
        
        # Launch KITTI
        # KITTI.set_autopilot(True)
            
        agent.set_destination(agent_waypoint[0])
        print('new destination: Location(x=%.1f, y=%.1f, z=%.1f)'
              %(agent_waypoint[0].x, agent_waypoint[0].y, agent_waypoint[0].z) )    
            
        # Pass to the next simulator frame to spawn sensors and to retrieve first data
        world.tick()
        
        start_record = time.time()
        cnt_waypoint = 0
        
        while True:
            world.tick()
            if agent.done():
                cnt_waypoint += 1
                agent.set_destination(agent_waypoint[cnt_waypoint])
                print('new destination: Location(x=%.1f, y=%.1f, z=%.1f)'
                    %(agent_waypoint[cnt_waypoint].x, agent_waypoint[cnt_waypoint].y, agent_waypoint[cnt_waypoint].z) )
                
            if agent.done():
                print("The target has been reached, stopping the simulation")
                break
            
            control = agent.run_step()
            control.manual_gear_shift = False
            KITTI.apply_control(control)
            
            
        print('Destroying KITTI')
        client.apply_batch([carla.command.DestroyActor(x) for x in actor_list])
        actor_list.clear()
            
        print("Elapsed time : ", time.time()-start_record)
        print()
            
        time.sleep(2.0)
            
        
    finally:
        print("Elapsed total time : ", time.time()-start_record_full)
        world.apply_settings(init_settings)
        
        time.sleep(2.0)
        
if __name__ == '__main__':
    main()