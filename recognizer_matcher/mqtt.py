import paho.mqtt.client as paho
import time


def on_connect(client, userdata, flags, rc):
    time.sleep(1)
    print("Connected With Result Code {}".format(rc))
    if rc == 0:
        client.connected_flag = True


def on_disconnect(client, userdata, rc):
    print("Disconnected From Broker")


def paho_start(client_id, clean_session):
    paho.Client.connected_flag = False
    client = paho.Client(client_id, clean_session)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    return client
