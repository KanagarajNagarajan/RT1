#include "ros/ros.h"
#include "geometry_msgs/Twist.h"
#include "nav_msgs/Odometry.h" 
#include <sstream>
#include <iostream>
#include "assignment1/Vel.h"
#include "my_srv2/Random.h"
double target_x = 0,target_y = 0;
ros::Publisher chatter_pub;
ros::ServiceClient client;
ros::Publisher pub2;

void subscriberCallback(const nav_msgs::Odometry::ConstPtr& pose_msg)
{
   ROS_INFO("Robot position: [%f, %f]", pose_msg->pose.pose.position.x, pose_msg->pose.pose.position.y);
   geometry_msgs::Twist vel;
   my_srv2::Random get_target
   double dx = target_x - pose_msg->pose.pose.position.x;
   double dy = target_y - pose_msg->pose.pose.position.y;
   if (pow(dx,2)+ pow(dy,2) <= pow(0.1,2)) {
     get_target.request.min = -6;
     get_target.request.max = 6;
     client.call(get_target);
     target_x = get_target.response.x;
     target_y = get_target.response.y;
     dx = target_x - pose_msg->pose.pose.position.x;
     dy = target_y - pose_msg->pose.pose.position.y;
   }
    double k = 1;
    vel.linear.x = k * dx; 
    vel.linear.y = k * dy;
    chatter_pub.publish(vel);
    assignment1::Vel mymsg;
    mymsg.name = "linear"; 
    mymsg.vx = vel.linear.x;
    mymsg.vy = vel.linear.y;
    pub2.publish(mymsg);
}

int main(int argc, char **argv)
{
  ros::init(argc, argv, "assignment1");
  ros::NodeHandle n;
  client = n.serviceClient<my_srv2::Random>("/random_target");
  chatter_pub = n.advertise<geometry_msgs::Twist>("cmd_vel", 1000);
  ros::Subscriber pose_sub = n.subscribe("odom", 1000, subscriberCallback);
  ros::spin();
    return 0;
}
