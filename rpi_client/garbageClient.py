'''*********************************************************************************
CLIENT - GARBAGE BIN
*********************************************************************************'''
#Import the Modules Required
import RPi.GPIO as GPIO
import time
import paho.mqtt.client as mqtt
import ConfigParser

#Importing the Config File and Parsing the file using the ConfigParser
config_file = "./config.ini"
Config = ConfigParser.ConfigParser()
Config.read(config_file)
logging.basicConfig(filename='logger.log',level=logging.DEBUG)

'''****************************************************************************************
Function Name 		:	ConfigSectionMap
Description		:	Parsing the Config File and Extracting the data and returning it
Parameters 		:	section - section to be parserd
****************************************************************************************'''
def ConfigSectionMap(section):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            logging.debug("exception on %s!" % option)
            dict1[option] = None
    return dict1

#Trigger Pin to be connected to the GPIO 23
TRIG = 23 
#Echo Pin to be connected to the GPIO 24
ECHO = 24

GARBAGE_ID = ConfigSectionMap("trashCan_id")['trashcan_1']
MQTT_SERVER_IP = ConfigSectionMap("mqtt_keys")['mqtt_server_ip']
MQTT_SERVER_PORT = ConfigSectionMap("mqtt_keys")['mqtt_server_port']
MQTT_CHANNEL = ConfigSectionMap("mqtt_keys")['mqtt_channel']
MQTT_ADDRESS = ConfigSectionMap("mqtt_keys")['mqtt_address']

'''****************************************************************************************

Function Name 		:	init
Description		:	Initalize the MQTT Protocol and connect to the host
Parameters 		:	None

****************************************************************************************'''
def init():
	global mqttc
	mqttc = mqtt.Client(MQTT_ADDRESS)
	mqttc.connect(MQTT_SERVER_IP,MQTT_SERVER_PORT)

'''****************************************************************************************

Function Name 		:	ultrasonicSensor_init
Description		:	Initalize the pins and set the Board Pins to BCM "Broadcom SOC channel"
Parameters 		:	None

****************************************************************************************'''
def ultrasonicSensor_init():
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(TRIG,GPIO.OUT)
	GPIO.setup(ECHO,GPIO.IN)
	GPIO.output(TRIG, False)
	
'''****************************************************************************************

Function Name 		:	distanceMeasurement
Description		:	Deducts the Distace and publishes to the MQTT Broker 
Parameters 		:	None

****************************************************************************************'''
def distanceMeasurement():
	l_prev_distance = 0
	while 1:
		ultrasonicSensor_init()
		time.sleep(2)		
		GPIO.output(TRIG, True)
		time.sleep(0.00001)
		GPIO.output(TRIG, False)
		#Starts the timer 
		while GPIO.input(ECHO)==0:
			pulse_start = time.time()
		#Waits for the timer to end once the pin is high
		while GPIO.input(ECHO)==1:
			pulse_end = time.time()

		pulse_duration = pulse_end - pulse_start

		l_distance = pulse_duration * 17150

		l_distance = round(l_distance, 2)

		if(l_prev_distance != l_distance and l_prev_distance > (l_distance+3) or l_prev_distance < (l_distance-3)):
			l_prev_distance = l_distance
			mqttc.publish(MQTT_CHANNEL, "{\"container\":\""+GARBAGE_ID+"\",\"level\":"+str(l_distance)+"}")
		print "Distance:",l_distance,"cm"
		GPIO.cleanup()

#Main - Script starts from here
if __name__ == '__main__':
	#Initialize the Script
	init()
	distanceMeasurement()

#End of the program