import logging
from tuya_connector import (
    TuyaOpenAPI,
    TuyaOpenPulsar,
    TuyaCloudPulsarTopic,
    TUYA_LOGGER,
)
import json
import signal

from ConfigurationReader import ConfigurationReader

import sys, time

class TuyaSecurityAlarmListener:
  confFile = "conf.json"
  
  conf = ConfigurationReader.Read(confFile)
  
  open_pulsar = None
  openapi = None

  ACCESS_ID = conf["access_id"]
  ACCESS_KEY = conf["access_key"]
  API_ENDPOINT = "https://openapi.tuyain.com"
  MQ_ENDPOINT = "wss://mqe.tuyain.com:8285/"
  
  def __init__(self):
    signal.signal(signal.SIGTERM, self.exit_gracefully)

  def exit_gracefully(self, signum, frame):
    # Stop Message Queue
    self.open_pulsar.stop()
    
  def onEvent(self, msg):
    data = json.loads(msg)
    logging.info(data["status"][0]["code"])
    logging.info(data["status"][0]["value"])
    if ((data["status"][0]["code"] == "master_mode" and data["status"][0]["value"] == "sos") or (data["status"][0]["code"]  == "Urget_Push_Infor")):
      logging.info("Triggering!")
      self.openapi.post("/v1.0/iot-03/devices/d78da503444a411f41lwi3/commands", {"commands": [{"code": "switch_1", "value": True}]})
    
  def run(self):
    # Enable debug log
    #TUYA_LOGGER.setLevel(logging.DEBUG)

    # Init openapi and connect
    self.openapi = TuyaOpenAPI(self.API_ENDPOINT, self.ACCESS_ID, self.ACCESS_KEY)
    self.openapi.connect()


    # Init Message Queue
    self.open_pulsar = TuyaOpenPulsar(
        self.ACCESS_ID, self.ACCESS_KEY, self.MQ_ENDPOINT, TuyaCloudPulsarTopic.PROD
    )
    # Add Message Queue listener
    self.open_pulsar.add_message_listener(self.onEvent)

    # Start Message Queue
    self.open_pulsar.start()

if __name__ == '__main__':
  #logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
  app = TuyaSecurityAlarmListener()
  app.run()

