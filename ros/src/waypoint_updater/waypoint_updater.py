#!/usr/bin/env python

import rospy
from geometry_msgs.msg import PoseStamped
from styx_msgs.msg import Lane, Waypoint
import tf

import math

'''
This node will publish waypoints from the car's current position to some `x` distance ahead.
As mentioned in the doc, you should ideally first implement a version which does not care
about traffic lights or obstacles.
Once you have created dbw_node, you will update this node to use the status of traffic lights too.
Please note that our simulator also provides the exact location of traffic lights and their
current status in `/vehicle/traffic_lights` message. You can use this message to build this node
as well as to verify your TL classifier.
TODO (for Yousuf and Aaron): Stopline location for each traffic light.
'''

LOOKAHEAD_WPS = 200 # Number of waypoints we will publish. You can change this number


class WaypointUpdater(object):
    def __init__(self):
        rospy.init_node('waypoint_updater')

        self.current_pos = None
        self.roll = self.pitch = self.yaw = 0

        rospy.Subscriber('/current_pose', PoseStamped, self.pose_cb)
        # '/base_waypoints' repeatedly publishes a list of all waypoints for the track,
        # this includes waypoints both before and after the vehicle.
        rospy.Subscriber('/base_waypoints', Lane, self.waypoints_cb)

        # TODO: Add a subscriber for /traffic_waypoint and /obstacle_waypoint below
        #self.traffic_waypoint_sub = rospy.Subscriber('/traffic_waypoint', Waypoint ,self.traffic_cb)
        #self.obstacle_waypoint_sub = rospy.Subscriber('/obstacle_waypoint', Waypoint ,self.obstacle_cb)


        self.final_waypoints_pub = rospy.Publisher('final_waypoints', Lane, queue_size=1)

        # TODO: Add other member variables you need below


        rospy.spin()

    def pose_cb(self, msg):
        # TODO: Implement

        self.current_pos = msg.pos.position
        orientation = msg.pose.orientation

        (self.roll, self.pitch, self.yaw) = tf.transformations.euler_from_quaternion(
                [orientation.x, orientation.y, orientation.z, orientation.w])

    def waypoints_cb(self, waypoints):
        # TODO: Implement
        waypoints_final = Lane()
        base_wp = waypoints.waypoints

        ## Find the closest waypoint ## 
        distance = float('inf')
        closest_wp = 0
        for i in range(len(base_wp)):
            wp_pos = base_wp[i].pose.pose.position 
            dist = sqrt((wp_pos.x - self.current_pos.x)**2 + (wp_pos.y - self.current_pos.y)**2 + (wp_pos.z - self.current_pos.z)**2)
            if (dist < distance):
                distance = dist
                closest_wp = i 

        ## Test waypoint position ## 
        heading = atan2((wp_pos.y - self.current_pos.y), (wp_pos.x - self.current_pos.x))
        if abs(self.yaw - heading) > pi/4:
            closest_wp += 1

        ## Add heading waypoints ##
        waypoints_final.header.frame_id = ' '
        waypoints_final.header.stamp = rospy.Time(0)
        waypoints_final.waypoints = base_wp[next_wp: (next_wp + LOOKAHEAD_WPS)]
 
        self.final_waypoints_pub.publish(waypoints_final)
        

    def traffic_cb(self, msg):
        # TODO: Callback for /traffic_waypoint message. Implement
        pass

    def obstacle_cb(self, msg):
        # TODO: Callback for /obstacle_waypoint message. We will implement it later
        pass

    def get_waypoint_velocity(self, waypoint):
        return waypoint.twist.twist.linear.x

    def set_waypoint_velocity(self, waypoints, waypoint, velocity):
        waypoints[waypoint].twist.twist.linear.x = velocity

    def distance(self, waypoints, wp1, wp2):
        dist = 0
        dl = lambda a, b: math.sqrt((a.x-b.x)**2 + (a.y-b.y)**2  + (a.z-b.z)**2)
        for i in range(wp1, wp2+1):
            dist += dl(waypoints[wp1].pose.pose.position, waypoints[i].pose.pose.position)
            wp1 = i
        return dist


if __name__ == '__main__':
    try:
        WaypointUpdater()
    except rospy.ROSInterruptException:
        rospy.logerr('Could not start waypoint updater node.')