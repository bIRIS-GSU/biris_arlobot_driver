#!/usr/bin/python

#========================================
#
# EV3 ROS Driver edited by Theodore Cornelius Smith
# Filename: serial_proj.py
#
#========================================

# Import the serial
import serial

# Import the rospy module

import rospy

# Import ROS Msgs

from std_msgs.msg import Int8
from std_msgs.msg import UInt8MultiArray

from geometry_msgs.msg import Twist

from biris_arlobot_msgs.msg import ping_list


# Import ev3 driver messages
# Might use generic messages, but for now we need the header data
# to determine network integrity

# Dict for EV3 peripherals (sensors + motors)

p = {}

cs_pub = None

def init_ros_publishers():

	global cs_pub
	cs_pub =rospy.Publisher("arlobot/ping",ping_list,queue_size=10)

def publish_ping_sensor():

	global cs_pub
  	global startMarker, endMarker

	startMarker = '<'
	endMarker = '>'
  
 	ck = ""
  	x = 'z' # any value that is not an end- or startMarker
	byteCount = -1 # to allow for the fact that the last increment will be one too many
  	
  	# wait for the start character
  	while ord(x) != ord(startMarker):
		print("Tossing " + x)
		x = ser.read()
  
  	# save data until the end marker is found
	while ord(x) != ord(endMarker):
 	  	if ord(x) != ord(startMarker):
 	 		ck = ck + x 
 	 		byteCount += 1
 	 	x = ser.read()

	try:
		ck.remove('Arduino is ready')
	except:
		pass

	try:
		cs_pub.publish(map(int,ck.split('_')))
		#rospy.log_info("Publishing ping sensors...")
	except:
		print("Threw out bad serial response from Arduino\n")

def subscribe_cmd_vel(data):

	print("Message on topic arlobot/cmd_vel received\n")
	global p

	potential_left = (data.linear.x - data.angular.z)

	if potential_left > 1:
		potential_left = 1

	elif potential_left < -1:
		potential_left = -1

	potential_right = (data.linear.x + data.angular.z)

	if potential_right > 1:
		potential_right = 1

	elif potential_right < -1:
		potential_right = -1
	
	left = 127 * potential_left + 127
	right = 127 * potential_right + 127

	stri = "<" + str(int(left)) + "," + str(int(right)) + ">"
	
	print(stri)
	ser.write(stri)

def on_shutdown():

	global cs_pub

	cs_pub.unregister()

serPort = "/dev/ttyACM0"
baudRate = 9600
ser = serial.Serial(serPort, baudRate)
print "Serial port " + serPort + " opened  Baudrate " + str(baudRate)

# Main function
def arlo_driver():

	print "Initializing ROS node..."
	rospy.init_node('arlo_driver',anonymous=False)
	print "[OK]"

	print "Initializing ROS publishers"
	init_ros_publishers()
	print "[OK]"

	print "Initializing ROS Subscriber"
	s = rospy.Subscriber("arlobot/cmd_vel",Twist,subscribe_cmd_vel,queue_size=10)
	print "[OK]"

	rate = rospy.Rate(100) # 25Hz

	while not rospy.is_shutdown():	
	#	if s.get_num_connections() == 0:
		print "Publishing Ping sensors"
		publish_ping_sensor()
		

		rate.sleep()







if __name__ == '__main__':

	try:

		arlo_driver()

	except rospy.ROSInterruptException:

		pass


