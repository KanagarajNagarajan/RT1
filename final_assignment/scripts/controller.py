#! /usr/bin/env python

# import ros stuff
"""
This node is managing each states as following below:
state0 - This node calls for /random_target in order to get random target position among [(-4,-3),(-4,2),(-4,7),(5,-7),(5,-3),(5,1)], and publishes the target position for /move_base. 
         After that, the robot starts to move for target.(this behaivor doens't depend on this node)
         When the robot arrives at the target position, it switches to state1.

state1 -  When the robot arrives the target,this node calls for /ask_user_interface. and publishes the target position /ask_user_interface gives for /move_base. 
          After that, the robot starts to move for target.(this behaivor doens't depend on this node)
          When the robot arrives at the target position, it switches to state2.

state2 -  When the robot arrives the target, the node calls for /wall_follower. 
          After the robot run around the map, it switches to state3.

state3 -  When the robot arrives the target user_interface gave, the robot just stops.
"""

import rospy
import time
from geometry_msgs.msg import Point
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
from std_srvs.srv import *
from move_base_msgs.msg import MoveBaseActionGoal
from geometry_msgs.msg import Twist
from tf import transformations
import random

import math
exit_position_ = False # For state 2 and 3,By this boolean variable,I can check if I already exited from the last position or not.
pub_target = None # the instance of publisher of target for /move_base
pub_vel = None # the instance of publisher of cmd_vel for /gazebo

#service clients
srv_client_random_target_ = None
srv_client_ask_user_interface_= None
srv_client_wall_follower_ = None
yaw_ = 0
# torelances
pos_error_allowed = 1
yaw_error_allowed_ = 5 * (math.pi / 180)  # 360 degrees

position_ = Point()
desired_position_ = Point()
desired_yaw_ = 1
desired_position_.x = rospy.get_param('des_pos_x')
desired_position_.y = rospy.get_param('des_pos_y')
desired_position_.z = 0
regions_ = None
state_desc_ = ['0: moving to random target.','1: ask user_interface and move to request position','2: wall following', '3: reached the last position']
state_ = -1
# 0 - setting random target
# 1 - asking userinterface
# 2 - start following the external walls
# 3 - stop in the last position

# service callback
def clbk_odom(msg):
    global position_, yaw_ 

    #gmapping_odom

    # position_ = msg.linear
    # yaw_ = msg.angular.z

    # /odom
    position_ = msg.pose.pose.position

    # yaw
    quaternion = (
        msg.pose.pose.orientation.x,
        msg.pose.pose.orientation.y,
        msg.pose.pose.orientation.z,
        msg.pose.pose.orientation.w)
    euler = transformations.euler_from_quaternion(quaternion)
    yaw_ = euler[2]

def clbk_laser(msg):
    global regions_
    regions_ = {
        'right':  min(min(msg.ranges[0:143]), 10),
        'fright': min(min(msg.ranges[144:287]), 10),
        'front':  min(min(msg.ranges[288:431]), 10),
        'fleft':  min(min(msg.ranges[432:575]), 10),
        'left':   min(min(msg.ranges[576:719]), 10),
    }
def stop_():
    global pub_vel
    twist_msg = Twist()
    twist_msg.linear.x = 0
    twist_msg.angular.z = 0
    pub_vel.publish(twist_msg)
    print("Stop!")

# set the target position and publish for /move_base
def set_target():
    global pub_target,desired_position_
    Goal = MoveBaseActionGoal()
    Goal.goal.target_pose.header.frame_id = "map"
    Goal.goal.target_pose.pose.orientation.w =1
    Goal.goal.target_pose.pose.position.x =  rospy.get_param("des_pos_x")
    Goal.goal.target_pose.pose.position.y =  rospy.get_param("des_pos_y")
    pub_target.publish(Goal)
    print("Published new target!")
    desired_position_.x = rospy.get_param("des_pos_x")
    desired_position_.y = rospy.get_param("des_pos_y")

def change_state(state):
    global state_, state_desc_
    global srv_client_wall_follower_ ,pub_vel,pub_target,desired_position_ ,desired_yaw_
    state_ = state
    log = "state changed: %s" % state_desc_[state]
    rospy.loginfo(log)
    if state_ == 0:
        resp = srv_client_wall_follower_(False)
        resp = srv_client_random_target_() # call the service node of random target
        set_target()
    if state_ == 1:
        resp = srv_client_wall_follower_(False)
        resp = srv_client_ask_user_interface_() # call the service node of ask_user_interface (and this service node contains the checker if requests meet the feasible target position or not)
        set_target()
    if state_ == 2:
        resp = srv_client_wall_follower_(True)  # call the service node of wall_follower
    if state_ == 3:
        print("Finish!")
        resp = srv_client_wall_follower_(False)
        stop_()

def normalize_angle(angle):
    if(math.fabs(angle) > math.pi):
        angle = angle - (2 * math.pi * angle) / (math.fabs(angle))
    return angle  


def main():
    global pub_target,pub_vel,yaw_,desired_yaw_,yaw_error_allowed_ ,position_,desired_position_ ,pos_error_allowed,exit_position_,state_desc_,regions_,state_ 
    global srv_client_random_target_,srv_client_ask_user_interface_,srv_client_wall_follower_ 

    rospy.init_node('Controller')
    sub_laser = rospy.Subscriber('/scan', LaserScan, clbk_laser)
    # sub_odom = rospy.Subscriber('/gmapping_odom', Twist, clbk_odom) # I can get the correct coordinate with respect to map
    sub_odom = rospy.Subscriber('/odom', Odometry, clbk_odom)
    pub_target = rospy.Publisher('/move_base/goal', MoveBaseActionGoal, queue_size=1)
    pub_vel = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
    srv_client_random_target_ = rospy.ServiceProxy('/random_target', Empty)
    srv_client_ask_user_interface_ = rospy.ServiceProxy('/ask_user_interface', Empty)
    srv_client_wall_follower_ = rospy.ServiceProxy('/wall_follower_switch', SetBool)

    # initialize going to the point
    change_state(0)

    rate = rospy.Rate(20)
    while not rospy.is_shutdown():
        print("now state" + state_desc_[state_])
        print("Hi! We are reaching the target position: x = " +
            str(desired_position_.x) + ", y = " + str(desired_position_.y))
        print("now positon: x = " +
            str(position_.x) + ", y = " + str(position_.y))
        # print("error_yaw: " + str(err_yaw))   
        if regions_ == None:
            continue
        if state_ == 0:      
            # reaching the first random target             
            err_pos = math.sqrt(pow(desired_position_.y - position_.y,
                                    2) + pow(desired_position_.x - position_.x, 2))
            if err_pos < pos_error_allowed :
                change_state(1)
            # (I don't consider the orientation when the robot arrived at target position)
        elif state_ == 1:  
            # reaching the second requested target                 
            err_pos = math.sqrt(pow(desired_position_.y - position_.y,
                                    2) + pow(desired_position_.x - position_.x, 2))
            if err_pos < pos_error_allowed :
                change_state(2)
        elif state_ == 2:
            # folloing wall
            err_pos = math.sqrt(pow(desired_position_.y - position_.y,
                                    2) + pow(desired_position_.x - position_.x, 2))
            """Once the robot exits from the destination position, it registered the robot already exited.
             By this, we can check if the robot went around the map or not when the robot is near the last position"""
            if err_pos >= pos_error_allowed/2:
                exit_position_ = True
                continue
            if err_pos < pos_error_allowed and exit_position_:
                change_state(3)
        rate.sleep()
    
if __name__ == '__main__':
    main()
