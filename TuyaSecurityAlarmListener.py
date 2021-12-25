"""This module has components that are used for testing tuya's device control and Pulsar massage queue."""
import logging
from tuya_connector import (
    TuyaOpenAPI,
    TuyaOpenPulsar,
    TuyaCloudPulsarTopic,
    TUYA_LOGGER,
)
import json

from ConfigurationReader import ConfigurationReader


def onEvent(msg):
	data = json.loads(msg)
	print(data["status"][0]["code"])
	print(data["status"][0]["value"])
	if ((data["status"][0]["code"] == "master_mode" and data["status"][0]["value"] == "sos") or (data["status"][0]["code"]  == "Urget_Push_Infor")):
		openapi.post("/v1.0/iot-03/devices/62480723f4cfa27f811c/commands", {"commands": [{"code": "switch_led", "value": True}]})

confFile = "conf.json"

conf = ConfigurationReader.Read(confFile)

ACCESS_ID = conf["access_id"]
ACCESS_KEY = conf["access_key"]
API_ENDPOINT = "https://openapi.tuyain.com"
MQ_ENDPOINT = "wss://mqe.tuyain.com:8285/"

# Enable debug log
#TUYA_LOGGER.setLevel(logging.DEBUG)

# Init openapi and connect
openapi = TuyaOpenAPI(API_ENDPOINT, ACCESS_ID, ACCESS_KEY)
openapi.connect()


# Init Message Queue
open_pulsar = TuyaOpenPulsar(
    ACCESS_ID, ACCESS_KEY, MQ_ENDPOINT, TuyaCloudPulsarTopic.PROD
)
# Add Message Queue listener
open_pulsar.add_message_listener(onEvent)

# Start Message Queue
open_pulsar.start()

input()
# Stop Message Queue
open_pulsar.stop()

