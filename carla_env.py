import carla
import random
import numpy as np

class Environment:

    def __init__(self, world='Town02_Opt', host='localhost', port=2000, tm_port=8000):
        # Connect to the server
        self.client = carla.Client(host, port)
        TIMEOUT_WAIT=10
        self.client.set_timeout(TIMEOUT_WAIT)

        # Load map
        self.world = self.client.load_world(world)

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
        self.TM_PORT = tm_port    #https://carla.readthedocs.io/en/latest/adv_traffic_manager/
        self.traffic_manager = self.client.get_trafficmanager(self.TM_PORT)
        self.traffic_manager.set_synchronous_mode(True)

        # Set a seed so behaviour is deterministic
        TM_SEED = 0
        self.traffic_manager.set_random_device_seed(TM_SEED)
        random.seed(TM_SEED)

        # Tracking all actors
        self.actor_ego = []
        self.actor_sensors = []
        self.actor_vehicles = []

        print("CARLA initialitaion complete.")

    def init_ego(self):
        """Initializes the ego vehicle including its sensor setup
        """

        self.RGB_EGO_WIDTH=1024
        self.RGB_EGO_HEIGHT=1024
        self.RGB_FOV=105

        # Choose vehicle model
        self.vehicle_bp = self.bp_lib.find('vehicle.tesla.model3')

        # Configure RGB sensor for ego perspective
        self.rgb_cam_bp = self.bp_lib.find('sensor.camera.rgb')

        self.rgb_cam_bp.set_attribute('image_size_x', f'{self.RGB_EGO_WIDTH}')
        self.rgb_cam_bp.set_attribute('image_size_y', f'{self.RGB_EGO_HEIGHT}')
        self.rgb_cam_bp.set_attribute('fov',  f'{self.RGB_FOV}')

        self.rgb_ego_location = carla.Location(2,0,1)
        self.rgb_ego_rotation = carla.Rotation(-10,0,0)
        self.rgb_ego_transform = carla.Transform(self.rgb_ego_location,self.rgb_ego_rotation)

        # Storing sensor data
        self.rgb_ego = []

        # Spawn ego vehicle
        transform = random.choice(self.spawn_points)
        self.ego_vehicle = self.world.spawn_actor(self.vehicle_bp, transform)
        self.actor_ego.append(self.ego_vehicle)

        # Set autopilot mode
        self.ego_vehicle.set_autopilot(True,self.TM_PORT)

        # Attach and listen to RGB Ego sensor
        self.rgb_ego = self.world.spawn_actor(self.rgb_cam_bp, self.rgb_ego_transform, attach_to=self.ego_vehicle, attachment_type=carla.AttachmentType.Rigid)
        self.actor_sensors.append(self.rgb_ego)
        self.rgb_ego.listen(lambda data: self.__process_rgb_ego_data(data))

        print("Ego vehicle initialization complete.")
    
    def populate(self):
        """Populate the world with vehicles which are in autopilot mode, controlled by the Traffic Manager
        """

        NUM_VEHICLES = 50
        max_vehicles = min([NUM_VEHICLES, len(self.spawn_points)])

        # Choose the vehicles models that should be spawned
        vehicle_bps = []
        for vehicle_bp in self.bp_lib.filter('*vehicle*'):
            vehicle_bps.append(vehicle_bp)

        # Take a random sample of the spawn points and spawn some vehicles
        for i, spawn_point in enumerate(random.sample(self.spawn_points, max_vehicles)):
            temp_vehicle = self.world.try_spawn_actor(random.choice(vehicle_bps), spawn_point)
            if temp_vehicle is not None:
                self.actor_vehicles.append(temp_vehicle)
                temp_vehicle.set_autopilot(True,self.TM_PORT)
        
        print("World populated with " + str(max_vehicles) + " vehicles.")  

    def __process_rgb_ego_data(self, image):
        """Observations directly viewable with OpenCV in CHW format.
        Change this processing if you want to use PyTorch, Pillow, PyGame, Matplotlib, ... 
        """
        
        i = np.array(image.raw_data)
        i2 = i.reshape((self.RGB_EGO_HEIGHT, self.RGB_EGO_WIDTH, 4))
        i3 = i2[:, :, :3]
        self.rgb_ego = i3





