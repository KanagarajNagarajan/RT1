#! /usr/bin/env python

# import ros stuff
"""
    This node works when the service "/ask_user_interface" is called as state0.
        -state 1:
            asking the request target on command line and checking if the request is feasible (among [[-4,-3],[-4,2],[-4,7],[5,-7],[5,-3],[5,1]]) or not
"""

import rospy
from std_srvs.srv import *
target_pos_lists = [[-4,-3],[-4,2],[-4,7],[5,-7],[5,-3],[5,1]]
# service callback


def set_new_pos(req):
    global target_pos_lists
    check_feasible_target = False #variable of checking  if it is feasible target or not
    print("Target reached! Please insert a new position among [[-4,-3],[-4,2],[-4,7],[5,-7],[5,-3],[5,1]]")
    while not check_feasible_target:
        x = float(raw_input('x :'))
        y = float(raw_input('y :'))
        for i in range(6):
            # If it is feasible target, then sets parameter for destination
            if x == target_pos_lists[i][0] and y == target_pos_lists[i][1]:
                check_feasible_target = True
                rospy.set_param("des_pos_x", x)
                rospy.set_param("des_pos_y", y)
                break
        # If not, try again.
        if not check_feasible_target:
            print("Sorry, the request position is not feasible...Please try again among [[-4,-3],[-4,2],[-4,7],[5,-7],[5,-3],[5,1]]")
    return []


def main():
    rospy.init_node('ask_user_interface')

    srv = rospy.Service('ask_user_interface', Empty, set_new_pos)
    rate = rospy.Rate(20)
    while not rospy.is_shutdown():
        rate.sleep()


if __name__ == '__main__':
    main()
