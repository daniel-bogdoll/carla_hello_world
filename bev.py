"""Adapted from https://github.com/zhejz/carla-roach/ CC-BY-NC 4.0 license."""
"""Adapted from https://github.com/wayveai/mile MIT license."""

import numpy as np
import cv2 as cv
from PIL import Image
import os

from carla_env import Environment

COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)

_width = 192
_margin = 100
_pixels_per_meter = float(5.0)
_pixels_ev_to_bottom = 40
_world_offset = None

def _world_to_pixel(location, projective=False):
        """Converts the world coordinates to pixel coordinates"""
        x = _pixels_per_meter * (location.x - _world_offset[0])
        y = _pixels_per_meter * (location.y - _world_offset[1])

        if projective:
            p = np.array([x, y, 1], dtype=np.float32)
        else:
            p = np.array([x, y], dtype=np.float32)
        return p

def _get_warp_transform(ev_loc, ev_rot):
        ev_loc_in_px = _world_to_pixel(ev_loc)
        yaw = np.deg2rad(ev_rot.yaw)

        forward_vec = np.array([np.cos(yaw), np.sin(yaw)])
        right_vec = np.array([np.cos(yaw + 0.5*np.pi), np.sin(yaw + 0.5*np.pi)])

        bottom_left = ev_loc_in_px - _pixels_ev_to_bottom * forward_vec - (0.5*_width) * right_vec
        top_left = ev_loc_in_px + (_width-_pixels_ev_to_bottom) * forward_vec - (0.5*_width) * right_vec
        top_right = ev_loc_in_px + (_width-_pixels_ev_to_bottom) * forward_vec + (0.5*_width) * right_vec

        src_pts = np.stack((bottom_left, top_left, top_right), axis=0).astype(np.float32)
        dst_pts = np.array([[0, _width-1],
                            [0, 0],
                            [_width-1, 0]], dtype=np.float32)
        return cv.getAffineTransform(src_pts, dst_pts)


def main():
    # CARLA Environment
    env = Environment(world="Town02_Opt", host="localhost", port=2000, tm_port=8000, timeout_wait=1000)
    env.init_ego()

    # World Offset
    waypoints = env.map.generate_waypoints(2) # list of carla.Waypoints
    route_map = waypoints
    min_x = min(waypoints, key=lambda x: x.transform.location.x).transform.location.x - _margin
    min_y = min(waypoints, key=lambda x: x.transform.location.y).transform.location.y - _margin
    global _world_offset
    _world_offset = np.array([min_x, min_y], dtype=np.float32)

    script_dir = os.path.dirname(os.path.realpath(__file__))
    i = 0

    try:
        while(True):
            env.world.tick()
            try:
                ev_transform = env.ego_vehicle.get_transform()
                ev_loc = ev_transform.location
                ev_rot = ev_transform.rotation
                M_warp = _get_warp_transform(ev_loc, ev_rot)

                # Route Mask
                route_mask = np.zeros([_width, _width], dtype=np.uint8)
                route_in_pixel = np.array([[_world_to_pixel(wp.transform.location)]
                                            for wp in route_map])
                route_warped = cv.transform(route_in_pixel, M_warp)
                cv.polylines(route_mask, [np.round(route_warped).astype(np.int32)], False, 1, thickness=16)
                route_mask = route_mask.astype(bool)

                # Convert the mask to an image and save it
                route_mask_img = Image.fromarray((route_mask * 255).astype(np.uint8), mode='L')
                filename = 'route_mask_{}.png'.format(i)
                route_mask_img.save(os.path.join(script_dir, filename))
                i += 1
                cv.waitKey(1)
            except:
                print("No observation")
    finally:
        for actor in env.actor_ego:
            actor.destroy()   
        for actor in env.actor_sensors:
            actor.destroy()
        for actor in env.actor_vehicles:
            actor.destroy()   
        print("All actors destroyed")

if __name__ == '__main__':
    main()