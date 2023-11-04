import carla
import random
import numpy as np

class Environment:

    def __init__(self, world='Town02_Opt', host='localhost', port=2000, tm_port=8000):
        self.client = carla.Client(host, port)              # Connect to the server
        TIMEOUT_WAIT=10                                     # Time the clients tries to find the server
        self.client.set_timeout(TIMEOUT_WAIT)       

        # Load map
        self.world = self.client.load_world(world)          # Load the chosen town. Towns with "_Opt" have layers, which can be removed (https://carla.readthedocs.io/en/0.9.14/core_map/)

        #Get blueprint library and spawn points
        self.bp_lib = self.world.get_blueprint_library()    # The blueprint library contains all assets that can be spawned (https://carla.readthedocs.io/en/0.9.14/bp_library/)
        self.map = self.world.get_map()                     # Loading the underlying map of the world, necessary to extract possible spawn points for vehicles in the scene
        self.spawn_points = self.map.get_spawn_points()     # Load all possible spawn points in the map

        # Set synchronous mode settings
        DELTA_SEC = 0.05                                    # Simulation time between two steps. Here: Twenty steps (1/0.05) to recreate one second
        self.settings = self.world.get_settings()           
        self.settings.synchronous_mode = True               # Activate synchronous mode, so the server waits for the client (https://carla.readthedocs.io/en/0.9.14/adv_synchrony_timestep/) 
        self.settings.fixed_delta_seconds = DELTA_SEC
        self.world.apply_settings(self.settings)

        # Set up the traffic manager
        self.TM_PORT = tm_port                              # Set port for the traffic manager (TM), necessary for all vehicles that are controlled by its autopilot mode
        self.traffic_manager = self.client.get_trafficmanager(self.TM_PORT)
        self.traffic_manager.set_synchronous_mode(True)

        # Set a seed so behaviour is deterministic
        TM_SEED = 0
        self.traffic_manager.set_random_device_seed(TM_SEED)
        random.seed(TM_SEED)

        # Tracking all actors, so they can be deleted when the script finishes
        self.actor_ego = []
        self.actor_sensors = []
        self.actor_vehicles = []

        print("CARLA initialitaion complete.")

    def init_ego(self):
        """Initializes the ego vehicle including its sensor setup
        """

        # Choose vehicle model
        self.vehicle_bp = self.bp_lib.find('vehicle.tesla.model3')

        # Configure RGB sensor for ego perspective
        self.RGB_EGO_WIDTH=1024                                                 # Resolution of a RGB camera (https://carla.readthedocs.io/en/0.9.14/ref_sensors/#rgb-camera)
        self.RGB_EGO_HEIGHT=1024
        self.RGB_FOV=105                                                        # Field of view parameter of the camera
        
        self.rgb_cam_bp = self.bp_lib.find('sensor.camera.rgb')                 # Choose sensor type (https://carla.readthedocs.io/en/0.9.14/ref_sensors/)

        self.rgb_cam_bp.set_attribute('image_size_x', f'{self.RGB_EGO_WIDTH}')  # Apply settings to sensor
        self.rgb_cam_bp.set_attribute('image_size_y', f'{self.RGB_EGO_HEIGHT}')
        self.rgb_cam_bp.set_attribute('fov',  f'{self.RGB_FOV}')

        self.rgb_ego_location = carla.Location(2,0,1)                           # Define transform in relation to a reference point, will be the ego vehicle later.
        self.rgb_ego_rotation = carla.Rotation(-10,0,0)
        self.rgb_ego_transform = carla.Transform(self.rgb_ego_location,self.rgb_ego_rotation)

        # Storing sensor data
        self.rgb_ego = []                                                       # We will listen to the sensor with a callback function, which can store its readings here

        # Spawn ego vehicle
        transform = random.choice(self.spawn_points)                            
        self.ego_vehicle = self.world.spawn_actor(self.vehicle_bp, transform)
        self.actor_ego.append(self.ego_vehicle)

        # Set autopilot mode with traffic manager
        self.ego_vehicle.set_autopilot(True,self.TM_PORT)

        # Attach and listen to RGB ego sensor
        self.rgb_ego = self.world.spawn_actor(self.rgb_cam_bp, self.rgb_ego_transform, attach_to=self.ego_vehicle, attachment_type=carla.AttachmentType.Rigid)
        self.actor_sensors.append(self.rgb_ego)                                 # Attach sensor to the ego vehicle
        self.rgb_ego.listen(lambda data: self.__process_rgb_ego_data(data))     # Define the callback function for the listener, where the camera data can be processed

        print("Ego vehicle initialization complete.")
    
    def populate(self):
        """Populate the world with vehicles which are in autopilot mode, controlled by the Traffic Manager
        """

        NUM_VEHICLES = 50
        max_vehicles = min([NUM_VEHICLES, len(self.spawn_points)])              # Don't spawn more vehicles than there are spawn points available

        # Choose the vehicles models that should be spawned
        vehicle_bps = []
        for vehicle_bp in self.bp_lib.filter('*vehicle*'):                      # Here we create a sublist of all assets in the blueprint library that are vehicles     
            vehicle_bps.append(vehicle_bp)

        # Take random sample of the spawn points, spawn vehicles, and activate their autopilot
        for i, spawn_point in enumerate(random.sample(self.spawn_points, max_vehicles)):
            temp_vehicle = self.world.try_spawn_actor(random.choice(vehicle_bps), spawn_point)  # Safety measure, as spawns can go wrong (https://carla.readthedocs.io/en/0.9.14/python_api/)
            if temp_vehicle is not None:
                self.actor_vehicles.append(temp_vehicle)
                temp_vehicle.set_autopilot(True,self.TM_PORT)
        
        print("World populated with " + str(max_vehicles) + " vehicles.")  

    def __process_rgb_ego_data(self, image):
        """Observations viewable with OpenCV in CHW (Channel, Height, Width) format.
        Change this processing if you want to use PyTorch, TensorFlow, Pillow, PyGame, Matplotlib, ... 
        """
        i = np.array(image.raw_data)
        i2 = i.reshape((self.RGB_EGO_HEIGHT, self.RGB_EGO_WIDTH, 4))
        i3 = i2[:, :, :3]
        self.rgb_ego = i3





