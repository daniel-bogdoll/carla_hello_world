import cv2

from carla_env import Environment

def main():
    env = Environment(world="Town02_Opt", host="172.31.240.1", port=2000, tm_port=8000)
    env.init_ego()
    env.populate()

    try:
        while(True):
            env.world.tick()
            try:
                cv2.imshow("RGB EGO", env.rgb_ego)
                cv2.waitKey(1)
            except:
                print("No observation")
    finally:
        cv2.destroyWindow("RGB EGO")
        for actor in env.actor_ego:
            actor.destroy()   
        for actor in env.actor_sensors:
            actor.destroy()
        for actor in env.actor_vehicles:
            actor.destroy()   
        print("All actors destroyed")

if __name__ == '__main__':
    main()