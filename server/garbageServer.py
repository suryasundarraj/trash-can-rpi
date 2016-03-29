'''*********************************************************************************
SERVER - GARBAGE BIN
*********************************************************************************'''
#Import the Modules Required
import paho.mqtt.client as mqtt
from pubnub import Pubnub
import ConfigParser
import logging
import json
import smtplib  

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

# Initialize the Pubnub Keys 
PUB_KEY = ConfigSectionMap("pubnub_init")['pub_key']
SUB_KEY = ConfigSectionMap("pubnub_init")['sub_key']

# Initialize the MQTT 
HOST_IP = ConfigSectionMap("mqtt_init")['host_ip']
CHANNEL_OBJECT = "garbaseData"

SENDER_MAIL_ID = ConfigSectionMap("email_user_settings")['user_email_id']
SENDER_PASSWORD = ConfigSectionMap("email_user_settings")['user_password']
RECEIVER_MAIL_ID = ConfigSectionMap("email_receiver_settings")['receiver_mail_id']
EMAIL_HOST_AND_PORT = ConfigSectionMap("email_user_settings")['host_and_port']
SUBJECT = "TRASH CAN WARNING"
TEXT = "Trash Can is Full"

# Prepare actual message
MESSAGE_TO_SEND = """\
Subject: %s

%s
""" % (SUBJECT, TEXT)

'''****************************************************************************************

Function Name 		:	mail_init
Description		:	Initilize the mail with the username and password 
Parameters 		:	none

****************************************************************************************'''
def mail_init():
	global server
	mail_connect = 0
	while mail_connect < 3:
		try:
			server = smtplib.SMTP(EMAIL_HOST_AND_PORT)
			server.starttls()
			server.login(SENDER_MAIL_ID,SENDER_PASSWORD)
			server.sendmail(SENDER_MAIL_ID,RECEIVER_MAIL_ID,MESSAGE_TO_SEND)
			server.quit()
			return None 
		except smtplib.SMTPException:
			print "Error: unable to Connect to email server"
			mail_connect += 1
	return None


'''****************************************************************************************

Function Name 		:	on_connect
Description		:	The callback for when the client receives a CONNACK response 
					from the server.
Parameters 		:	client - client id
					rc - flag

****************************************************************************************'''
def on_connect(client, userdata, rc):
	print("Connected with result code "+str(rc))
	# Subscribing in on_connect() means that if we lose the connection and
	# reconnect then subscriptions will be renewed.
	client.subscribe(CHANNEL_OBJECT)


'''****************************************************************************************

Function Name 		:	on_message
Description		:	The callback for when a PUBLISH message is received from the server.
Parameters 		:	client - client id
					msg = message received from the client

****************************************************************************************'''
# 
def on_message(client, userdata, msg):
	global server
	message = dict()
	message = json.loads(msg.payload)
	print message  
	pubnub.publish(channel="garbageApp-resp", message=message)
	if(message.has_key("level") and message["level"] <= 40):
		mail_init()
		print "Trash can is Full"


'''****************************************************************************************

Function Name 		:	init
Description		:	Initalize the MQTT Protocol, pubnub keys and Starts Subscribing 
					from the garbageApp-req channels
Parameters 		:	None

****************************************************************************************'''
def init():
	#Pubnub Initialization
	global pubnub,client 
	pubnub = Pubnub(publish_key=PUB_KEY,subscribe_key=SUB_KEY)
	client = mqtt.Client()
	client.on_connect = on_connect
	client.on_message = on_message

	client.connect(HOST_IP, 1883, 60)

	# Blocking call that processes network traffic, dispatches callbacks and
	# handles reconnecting.
	# Other loop*() functions are available that give a threaded interface and a
	# manual interface.
	client.loop_forever()

if __name__ == '__main__':
	#Initialize the Script
	init()



#End of the program
