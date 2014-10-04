#!/usr/bin/python
import acutrol
import roslib; roslib.load_manifest('acutrol')
import rospy
import json

from sensor_msgs.msg import JointState
from acutronics_driver.srv import SetRate, SetPosition

def poll_loop(table_object, rate_hz=20):
    publisher   = rospy.Publisher('/ac117', JointState)
    rate_keeper = rospy.Rate(rate_hz)
    msg         = JointState()
    msg.name    = ['rate_table']
    table_object.startup()
    while not rospy.is_shutdown():
        try:
            status           = table_object.status()
            msg.velocity     = status['velocity']
            msg.position     = status['position']
            msg.header.stamp = rospy.Time.now()
            publisher.publish(msg)
        except:
            pass
        rate_keeper.sleep()
    table_object.shutdown()

class ServiceHandlers:
    def __init__(self, table_object):
        self.table_object = table_object

    def handle_rate(self, rate):
        self.table_object.command_rate(rate.rate)
        return True

    def handle_position(self, position):
        self.table_object.command_position(position.position)
        return True

if __name__ == '__main__':
    table    = acutrol.AcutrolDevice()
    handlers = ServiceHandlers(table)

    rospy.init_node('AC117_node')
    set_rate     = rospy.Service('/AC117/SetRate', 
                                 SetRate, 
                                 handlers.handle_rate)
    set_position = rospy.Service('/AC117/SetPosition', 
                                 SetPosition, 
                                 handlers.handle_position)
    poll_loop(table_object=table)
