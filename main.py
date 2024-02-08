import cv2

from carla_env import Environment

def main():
    env = Environment(world="Town02_Opt", host="localhost", port=2000, tm_port=8000, timeout_wait=100)
    env.init_ego()
    env.populate()

    try:
        while(True):
            env.world.tick()
            try:
                cv2.imshow("RGB EGO", env.rgb_ego)
                cv2.waitKey(1)
            except Exception as error:
                print("An exception occurred:", error)

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