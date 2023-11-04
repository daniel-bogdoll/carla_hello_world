# carla_hello_world
First steps with CARLA 0.9.14

## Development in WSL2

Currently, WSL2 has no stable support for [GPU-accelerated Vulkan](https://github.com/microsoft/WSL/issues/7790). However, CARLA is [based on Vulkan](https://carla.readthedocs.io/en/0.9.14/adv_rendering_options/). Thus, CARLA will run on the CPU with lavapipe, when launched inside WSL2. I do not recommend continuing this way, but there are (experimental solutions)[https://github.com/microsoft/wslg/issues/40#issuecomment-1685123693].

### Run [CARLA under Windows](https://github.com/carla-simulator/Ccarla/issues/5806), then access it under WSL2

#### Launch CARLA

- Download [CARLA 0.9.14](https://carla-releases.s3.eu-west-3.amazonaws.com/Windows/CARLA_0.9.14.zip)
- Unzip it, access the `..\CARLA_0.9.14\WindowsNoEditor` folder with PowerShell
- Run `./CarlaUE4.exe -RenderOffScreen`

#### Setup Ubuntu 20.04 in WSL2

- Setup [WSL2 under Windows and install Ubuntu 20.04.6 LTS](https://ubuntu.com/tutorials/install-ubuntu-on-wsl2-on-windows-10#1-overview)
- Download [Visual Studio Code](https://code.visualstudio.com/) and install the `Remote Development` extensions
- Open VS Code, click on the bottom-left "Open a Remote Windows" Button and "Connect to WSL using Distro" and pick "Ubuntu-20.04"
- Setup an [SSH key](https://www.digitalocean.com/community/tutorials/how-to-set-up-ssh-keys-on-ubuntu-20-04) and connect it to [GitHub](https://github.com/settings/keys) / [GitLab](https://ids-git.fzi.de/-/profile/keys)
- `git clone` the repository you'll be working in and open its folder within VS Code

##### Venv
- Open a terminal and install `sudo apt install python3.8-venv`
- Setup a [venv](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/) in your project folder with `python3 -m venv env`
- Source the virtual environment with `source env/bin/activate`
- Update pip with `pip install --upgrade pip`
- Install the CARLA client with `pip install carla`
- Install all further necessary packages with `pip install PackageName`
- Once the project is fully configured, run `pip freeze > requirements.txt` to generate a dependencies list
- Create a ".gitignore" file where you put "env" in the first line to ignore all files within the venv

- Check if you can [access the default CARLA port 2000](https://superuser.com/questions/1679757/how-to-access-windows-localhost-from-wsl2) from within WSL2 with `nc -zv "$(hostname).local" 2000`. If not, it might be necessary to open the Ports [2000 and 2001](https://carla.readthedocs.io/en/0.9.14/start_quickstart/) in the Firewall.
- Run `ip route` in WSL2, the "default via" address is the address to use to access the Windows localhost, where CARLA is running. In the main.py file, update `env = Environment(host="172.31.240.1"...)`

## Development in Linux 20.04

- Download [CARLA 0.9.14](https://carla-releases.s3.eu-west-3.amazonaws.com/Linux/CARLA_0.9.14.tar.gz)
