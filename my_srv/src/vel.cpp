#include "ros/ros.h"
#include "my_srv/Velocity.h"
#include<math.h>
double pi = 3.141592;

bool oscillator(my_srv::Velocity::Request &req, my_srv::Velocity::Response &res){ 
    if (req.x >= 2 && req.x <= 9) res.x = 0.1 + 2*sin(pi*req.x/7-2*pi/7);
    else res.x = 1;
    return true; 
}

int main(int argc, char **argv)
{ 
    ros::init(argc, argv, "velocity_server");
    ros::NodeHandle n;
    ros::ServiceServer service= n.advertiseService("/velocity",oscillator); 
    ros::spin();

    return 0;
} 



// #include "ros/ros.h"
// #include "my_srv/Velocity.h"


// double randMToN(double M, double N)
// { return M+(rand()/(RAND_MAX/(N-M)));}

// bool myrandom (my_srv::Velocity::Request &req, my_srv::Velocity::Response &res){ 
//     res.x = randMToN(req.min, req.max);
//     res.z = randMToN(req.min, req.max);
//     return true; 
//     }

// int main(int argc, char **argv)
// { 
//     ros::init(argc, argv, "velocity_server");
//     ros::NodeHandle n;
//     ros::ServiceServer service= n.advertiseService("/velocity",myrandom); 
//     ros::spin();

//     return 0;
// } 