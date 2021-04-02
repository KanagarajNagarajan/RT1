#! /usr/bin/env python

# import ros stuff
"""
    This node works when the service "/random_target" is called as state0.
        -state 0:
            setting random target
"""

import rospy
from std_srvs.srv import *
import random
# service callback
target_pos_lists = [[-4,-3],[-4,2],[-4,7],[5,-7],[5,-3],[5,1]]

def set_random_pos(req):
    global target_pos_lists
    # generate random integer number in range from 0 to 5
    random_choice = random.randrange(6)
    # set parameter for destination cordinate
    rospy.set_param("des_pos_x", target_pos_lists[random_choice][0])
    rospy.set_param("des_pos_y", target_pos_lists[random_choice][1])
    print("Random target generated! x = " +
            str(target_pos_lists[random_choice][0]) + ", y = " + str(target_pos_lists[random_choice][1]))
    return []


def main():
    rospy.init_node('random_target')
    srv = rospy.Service('random_target', Empty, set_random_pos)
    rate = rospy.Rate(20)
    while not rospy.is_shutdown():
        rate.sleep()


if __name__ == '__main__':
    main()
