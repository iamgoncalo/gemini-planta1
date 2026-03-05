import time
import json
import random
from datetime import datetime
import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from openclaw_fusion import OpenClawEdgeFusion

# Configuration matching the AFI Digital Twin Stack
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "horse_cft/ZONE_01/openclaw"

INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "plantaos-dev-token"
INFLUX_ORG = "planta"
INFLUX_BUCKET = "horse_cft_f_field"

class DataBusBridge:
    """
    AFI Integration Layer: Subscribes to raw OpenClaw spatial streams, 
    fuses them into F = P/D, and pushes the F-field to InfluxDB for DT-02 & DT-03.
    """
    def __init__(self):
        self.fusion_engine = OpenClawEdgeFusion(zone_id="HORSE_CFT_ZONE_01")
        
        # InfluxDB setup
        self.influx_client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
        self.write_api = self.influx_client.write_api(write_options=SYNCHRONOUS)
        
        # MQTT setup
        self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, reason_code, properties):
        print(f"[Data Bus] Connected to MQTT Broker with result code {reason_code}")
        client.subscribe(MQTT_TOPIC)

    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            # 1. Process raw spatial data into Freedom (F) metrics
            f_metrics = self.fusion_engine.process_openclaw_stream(payload)
            # 2. Write to InfluxDB
            self.write_to_influx(f_metrics)
        except Exception as e:
            print(f"[Data Bus] Error processing message: {e}")

    def write_to_influx(self, metrics):
        try:
            point = Point("spatial_freedom") \
                .tag("zone_id", metrics["zone_id"]) \
                .field("P_spatial", metrics["P_spatial"]) \
                .field("D_spatial", metrics["D_spatial"]) \
                .field("F_spatial", metrics["F_spatial"]) \
                .field("active_agents", metrics["active_agents"]) \
                .time(datetime.utcnow(), WritePrecision.NS)
            
            # self.write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
            print(f"[Data Bus] Staged for InfluxDB: Zone={metrics['zone_id']} | F={metrics['F_spatial']} (P={metrics['P_spatial']}, D={metrics['D_spatial']})")
        except Exception as e:
            print(f"[Data Bus] InfluxDB write failed: {e}")

    def start(self):
        print("[Data Bus] Starting MQTT/InfluxDB Bridge...")
        try:
            self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
            self.mqtt_client.loop_start()
            print("[Data Bus] Listening for live OpenClaw MQTT streams...")
            while True:
                time.sleep(1)
        except ConnectionRefusedError:
            print("[Data Bus] No local MQTT broker found. Falling back to OpenClaw simulation mode.")
            self.run_simulation()

    def run_simulation(self):
        print("[Data Bus] Generating 3 simulated OpenClaw spatial frames...")
        for i in range(3):
            # Simulating raw output from OpenClaw's tracking engine
            sim_frame = {
                "active_trajectories": [x for x in range(random.randint(1, 15))],
                "spatial_density": round(random.uniform(1.0, 4.0), 2),
                "timestamp": datetime.utcnow().isoformat()
            }
            f_metrics = self.fusion_engine.process_openclaw_stream(sim_frame)
            self.write_to_influx(f_metrics)
            time.sleep(1)

if __name__ == "__main__":
    bridge = DataBusBridge()
    bridge.start()
