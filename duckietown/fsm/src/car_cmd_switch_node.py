#!/usr/bin/env python
'''
Author: Shih-Yuan Liu
'''

import rospy
from duckietown_msgs.msg import Twist2DStamped, FSMState

class SwitchNode(object):
    def __init__(self,msg_type):
        self.node_name = rospy.get_name()
        # Read parameters
        self.mappings = rospy.get_param("~mappings")
        source_topic_dict = rospy.get_param("~source_topics")
        self.current_src_name = None

        # Construct publisher
        self.pub_cmd = rospy.Publisher("~cmd",msg_type,queue_size=1)
        
        # Construct subscribers
        self.sub_fsm_state = rospy.Subscriber(rospy.get_param("~mode_topic"),FSMState,self.cbFSMState)

        # Construct subscribers
        self.sub_dict = dict()
        for src_name, topic_name in source_topic_dict.items():
            self.sub_dict[src_name] = rospy.Subscriber(topic_name,msg_type,self.cbWheelsCmd,callback_args=src_name)

        rospy.loginfo("[%s] Initialized. " %(self.node_name))
        
    def cbFSMState(self,fsm_state_msg):
        self.current_src_name = self.mappings.get(fsm_state_msg.state)
        if self.current_src_name is None:
            rospy.logwarn("[%s] FSMState %s not handled. No msg pass through the switch." %(self.node_name,fsm_state_msg.state))

    def cbWheelsCmd(self,msg,src_name):
        if src_name == self.current_src_name:
            self.pub_cmd.publish(msg)

    def on_shutdown(self):
        rospy.loginfo("[%s] Shutting down." %(self.node_name))

if __name__ == '__main__':
    # Initialize the node with rospy
    rospy.init_node('car_cmd_switch_node', anonymous=False)
    # Create the DaguCar object
    node = SwitchNode(msg_type=Twist2DStamped)
    # Setup proper shutdown behavior 
    rospy.on_shutdown(node.on_shutdown)
    # Keep it spinning to keep the node alive
    rospy.spin()
