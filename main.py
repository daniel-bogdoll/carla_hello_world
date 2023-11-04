import cv2

from carla_env import Environment

def main():
    env = Environment(world="Town02_Opt", host="172.31.240.1", port=2000)
    env.init_ego()
    env.reset()
    try:
        while(True):
            env.world.tick()
            try:
                cv2.imshow("", env.observation)
                cv2.waitKey(1)
            except:
                print("No observation")
    finally:
        for actor in env.actor_list:
            actor.destroy()   
        print("All actors destroyed")
        
if __name__ == '__main__':
    main()