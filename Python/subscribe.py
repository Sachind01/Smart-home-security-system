import paho.mqtt.client as mqtt
import time

def on_message(client , userdata , message):
    print("Received Message: ", str(message.payload.decode("utf-8")))

mqttBroker = "mqtt.eclipseprojects.io"
client = mqtt.Client("out")
client.connect(mqttBroker)

client.loop_start()
client.subscribe("out")
client.on_message = on_message
time.sleep(30)
client.loop_stop()
