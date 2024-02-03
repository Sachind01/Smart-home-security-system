import gesture
import paho.mqtt.client as mqtt
import time
from random import randrange , uniform

mqttBroker = "mqtt.eclipseprojects.io"
client = mqtt.Client("out")
client.connect(mqttBroker)


while True:
    
    client.publish(out)
    print(out)
    time.sleep(1)
