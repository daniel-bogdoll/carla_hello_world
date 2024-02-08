# Hello World, CARLA 0.9.14!

This repository contains two branches. In the **main** branch, the ego vehicle is controlled with an Autopilot. In the more complex branch **routemap**, a route is computed on the map and a controlled is used to follow it. In addition, this planned route is visualized on a Bird's-Eye-View map.

## Setup
### Development in WSL2

Currently, WSL2 has no stable support for [GPU-accelerated Vulkan](https://github.com/microsoft/WSL/issues/7790). However, CARLA is [based on Vulkan](https://carla.readthedocs.io/en/0.9.14/adv_rendering_options/). Thus, CARLA will run on the CPU with lavapipe, when launched inside WSL2. I do not recommend continuing this way, but there are [experimental solutions](https://github.com/microsoft/wslg/issues/40#issuecomment-1685123693). Here, we will launch the CARLA server in Windows and connect to it with a CARLA client in our WSL2 Ubuntu session.

#### Launch CARLA in Windows

- Download [CARLA 0.9.14](https://carla-releases.s3.eu-west-3.amazonaws.com/Windows/CARLA_0.9.14.zip) in Windows
- Unzip it, access the `..\CARLA_0.9.14\WindowsNoEditor` folder with PowerShell
- Run `./CarlaUE4.exe -RenderOffScreen -carla-rpc-port=2000`

#### Setup Ubuntu 20.04 in WSL2

- Setup [WSL2 for Windows and install Ubuntu 20.04.6 LTS](https://ubuntu.com/tutorials/install-ubuntu-on-wsl2-on-windows-10#1-overview)
- Download [Visual Studio Code](https://code.visualstudio.com/) and install the [Remote Development](https://code.visualstudio.com/docs/remote/remote-overview) extensions
- Open VS Code, click on the bottom-left "Open a Remote Windows" Button, choose "Connect to WSL using Distro" and pick "Ubuntu-20.04"
- Setup an [SSH key](https://www.digitalocean.com/community/tutorials/how-to-set-up-ssh-keys-on-ubuntu-20-04) inside Ubuntu and connect it to [GitHub](https://github.com/settings/keys)
- Run `git clone git@github.com:daniel-bogdoll/carla_hello_world.git` and open it within VS Code

##### Setup your virtual environment
- Open a terminal inside Ubuntu and navigate into the root folder of this repository
- Run `sudo apt install python3.8-venv` to make [virtual environments (venv)](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/) available
- Setup your venv with `python3 -m venv env`
- Source the virtual environment with `source env/bin/activate`
- Update pip with `pip install --upgrade pip`
- Install all necessary packages with `pip install -r requirements.txt`

##### Connect to CARLA
- Check if you can [access the default CARLA port 2000](https://superuser.com/questions/1679757/how-to-access-windows-localhost-from-wsl2) from within WSL2 with `nc -zv "$(hostname).local" 2000`
- If not, it might be necessary to open the ports [2000 and 2001](https://carla.readthedocs.io/en/0.9.14/start_quickstart/) in the Firewall.
- Run `ip route` in WSL2, the `default via` is the IP address of the Windows localhost, where CARLA is running.
- In the main.py file, update `env = Environment(host="172.31.240.1"...)` accordingly

## Code Structure

#### main.py

The main file first initializes the whole scenario, which will be explained in the next section:
```
def main():
    env = Environment(world="Town02_Opt", host="172.31.240.1", port=2000, tm_port=2500)
    env.init_ego()
    env.populate()
```

Then, the main loop starts, where a tick is sent to the server, allowing it to continue. This is part of the [synchronous mode](https://carla.readthedocs.io/en/0.9.14/adv_synchrony_timestep/), which is activated here. In addition, observations from a RGB camera data are being visualized with OpenCV:

```
try:
  while(True):
    env.world.tick()
    try:
      cv2.imshow("RGB EGO", env.rgb_ego)
      cv2.waitKey(1)
    except:
      print("No observation")
```

Finally, all actors spawned in the simulation are being destroyed, so we can continue using the server when we restart the script:
```
finally:
  cv2.destroyWindow("RGB EGO")
  for actor in env.actor_ego:
    actor.destroy()   
  for actor in env.actor_sensors:
    actor.destroy()
  for actor in env.actor_vehicles:
    actor.destroy()   
```

#### carla_env.py
Here, the whole CARLA environment is being managed. The code is excessively commented, which is why I'd recommend to just look into it :)

