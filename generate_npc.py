import glob
import os
import sys
from pathlib import Path

try:
    sys.path.append(glob.glob('/home/junhakim/CARLA/PythonAPI/carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
    
    sys.path.append(glob.glob('../../')[0])

except IndexError:
    pass

import carla
from carla import VehicleLightState as vls

import numpy as np
import logging
import random

# class vehicle_npc():
#     def __init__(self, vehicle=None):
#         self.vehilce = vehicle

def spawn_npc(client, vehicles_list, vehicle_model, spawn_point):
        world = client.get_world()

        traffic_manager = client.get_trafficmanager()
        traffic_manager.set_global_distance_to_leading_vehicle(1.0)
        
        #traffic_manager.set_hybrid_physics_mode(True)
        #traffic_manager.set_random_device_seed(args.seed)

        traffic_manager.set_synchronous_mode(True)
        synchronous_master = True

        blueprint = world.get_blueprint_library().filter(vehicle_model)[0]

        # @todo cannot import these directly.
        SpawnActor = carla.command.SpawnActor
        SetAutopilot = carla.command.SetAutopilot
        SetVehicleLightState = carla.command.SetVehicleLightState
        FutureActor = carla.command.FutureActor

        # --------------
        # Spawn vehicles
        # --------------
        batch = []

        if blueprint.has_attribute('color'):
                color = random.choice(blueprint.get_attribute('color').recommended_values)
                blueprint.set_attribute('color', color)
        if blueprint.has_attribute('driver_id'):
                driver_id = random.choice(blueprint.get_attribute('driver_id').recommended_values)
                blueprint.set_attribute('driver_id', driver_id)
        blueprint.set_attribute('role_name', 'autopilot')
        # prepare the light state of the cars to spawn
        light_state = vls.NONE
        car_lights_on = False
        if car_lights_on:
                light_state = vls.Position | vls.LowBeam | vls.LowBeam
        # spawn the cars and set their autopilot and light state all together
        batch.append(SpawnActor(blueprint, spawn_point)
                .then(SetAutopilot(FutureActor, True, traffic_manager.get_port()))
                .then(SetVehicleLightState(FutureActor, light_state)))
        print('spawn vehicle: '+vehicle_model)
        print('-> spawn point: x=%1f, y=%1f, z=%1f' %(spawn_point.location.x, spawn_point.location.y, spawn_point.location.z))
        
        vehicle = world.spawn_actor(blueprint, spawn_point)
        vehicle.set_autopilot = True

        # for response in client.apply_batch_sync(batch, synchronous_master):
        #         if response.error:
        #                 logging.error(response.error)
        #         else:
        #                 vehicles_list.append(response.actor_id)
                        
        # example of how to use parameters
        traffic_manager.global_percentage_speed_difference(30.0)
        
        return vehicle
        
        