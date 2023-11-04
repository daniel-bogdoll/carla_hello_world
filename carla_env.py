import carla
import random
import numpy as np

class Environment:

    def __init__(self, world='Town02_Opt', host='localhost', port=2000):
        # Connect to the server
        self.client = carla.Client(host, port)
        TIMEOUT_WAIT=10
        self.client.set_timeout(TIMEOUT_WAIT)

        # Load map
        self.world = self.client.load_world(world)

        # Unload map layers https://carla.readthedocs.io/en/latest/core_map/#carla-maps
        self.world.unload_map_layer(carla.MapLayer.All)

        #Get blueprint library and spawn points
        self.bp_lib = self.world.get_blueprint_library()
        self.map = self.world.get_map()
        self.spawn_points = self.map.get_spawn_points()

        # Set synchronous mode settings
        DELTA_SEC = 0.05    #the simulator will take twenty steps (1/0.05) to recreate one second of the simulated world
        self.settings = self.world.get_settings()
        self.settings.synchronous_mode = True 
        self.settings.fixed_delta_seconds = DELTA_SEC
        self.world.apply_settings(self.settings)

        self.client.reload_world(False) # reload map keeping the world settings

        # Set up the traffic manager
        self.TM_PORT = 8000    #https://carla.readthedocs.io/en/latest/adv_traffic_manager/
        self.traffic_manager = self.client.get_trafficmanager(self.TM_PORT)
        self.traffic_manager.set_synchronous_mode(True)

        # Set a seed so behaviour is deterministic
        TM_SEED = 0
        self.traffic_manager.set_random_device_seed(TM_SEED)
        random.seed(TM_SEED)

        # Tracking all actors
        self.actor_list = []

        print("CARLA initialitaion complete.")

    def init_ego(self):
        BEV_DISTANCE = 10
        self.IM_WIDTH=1024
        self.IM_HEIGHT=1024

        # Choose vehicle model
        self.vehicle_bp = self.bp_lib.find('vehicle.tesla.model3')

        # Configure semantic segmentation sensor for BEV perspective
        self.ss_camera_bp = self.bp_lib.find('sensor.camera.semantic_segmentation')

        self.ss_camera_bp.set_attribute('image_size_x', f'{self.IM_WIDTH}')
        self.ss_camera_bp.set_attribute('image_size_y', f'{self.IM_HEIGHT}')
        self.ss_camera_bp.set_attribute('fov', '110')

        self.ss_cam_location = carla.Location(0,0,BEV_DISTANCE)
        self.ss_cam_rotation = carla.Rotation(-90,0,0)
        self.ss_cam_transform = carla.Transform(self.ss_cam_location, self.ss_cam_rotation)

        # Configure collision sensor to detect collisions
        self.col_sensor_bp = self.bp_lib.find('sensor.other.collision')

        self.col_sensor_location = carla.Location(0,0,0)
        self.col_sensor_rotation = carla.Rotation(0,0,0)
        self.col_sensor_transform = carla.Transform(self.col_sensor_location, self.col_sensor_rotation)

        # Accessing sensor data
        self.observation = []
        self.collision_hist = []

        print("Ego vehicle initialitaion complete.")

    def reset(self):
        for actor in self.actor_list:
            actor.destroy()

        self.actor_list = []
        self.collision_hist = []

        # Spawn ego vehicle
        transform = random.choice(self.spawn_points)
        self.vehicle = self.world.spawn_actor(self.vehicle_bp, transform)
        self.actor_list.append(self.vehicle)

        # Set autopilot mode
        self.vehicle.set_autopilot(True,self.TM_PORT)

        # Attach and listen to image sensor (BEV Semantic Segmentation)
        self.ss_cam = self.world.spawn_actor(self.ss_camera_bp, self.ss_cam_transform, attach_to=self.vehicle, attachment_type=carla.AttachmentType.Rigid)
        self.actor_list.append(self.ss_cam)
        self.ss_cam.listen(lambda data: self.__process_ss_cam_data(data))

        # Attach and listen to collision sensor
        self.col_sensor = self.world.spawn_actor(self.col_sensor_bp, self.col_sensor_transform, attach_to=self.vehicle)
        self.actor_list.append(self.col_sensor)
        self.col_sensor.listen(lambda event: self.__process_collision_data(event))

        print("Reset complete.")
    
    def __process_ss_cam_data(self, image):
        """ Observations directly viewable with OpenCV in CHW format """
        image.convert(carla.ColorConverter.CityScapesPalette)
        i = np.array(image.raw_data)
        i2 = i.reshape((self.IM_HEIGHT, self.IM_WIDTH, 4))
        i3 = i2[:, :, :3]
        self.observation = i3

    def __process_collision_data(self, event):
        self.collision_hist.append(event)





