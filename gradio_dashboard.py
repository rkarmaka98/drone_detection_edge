#!/usr/bin/env python3
import gradio as gr
import paho.mqtt.client as mqtt
from PIL import Image
import io
import pandas as pd
import json
import time

class DetectionDashboard:
    def __init__(self):
        self.latest_image = None
        self.detections = []
        self.mqtt_client = self.setup_mqtt()
    
    def setup_mqtt(self):
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "dashboard")
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        
        connected = False
        while not connected:
            try:
                client.connect("localhost", 1883)
                client.loop_start()
                connected = True
            except Exception as e:
                print(f"Connection failed: {e}. Retrying...")
                time.sleep(2)
        
        return client
    
    def on_connect(self, client, userdata, flags, rc, properties):
        print("Connected to MQTT")
        client.subscribe("openmv/detections")
    
    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload)
            img_bytes = bytes.fromhex(payload["image"])
            self.latest_image = Image.open(io.BytesIO(img_bytes))
            
            self.detections.append({
                "Time": payload["timestamp"],
                "Label": payload["label"],
                "Score": f"{float(payload['score']):.2f}",
                "BBox": str(payload["bbox"])
            })
            
            if len(self.detections) > 50:
                self.detections.pop(0)
        except Exception as e:
            print(f"Message processing error: {e}")
    
    def get_detections(self):
        if not self.latest_image:
            return None, pd.DataFrame(columns=["Time", "Label", "Score", "BBox"])
        return self.latest_image, pd.DataFrame(self.detections)

def create_interface():
    dashboard = DetectionDashboard()
    
    with gr.Blocks(title="Drone Detection") as app:
        gr.Markdown("# 🚁 Real-time Drone Detection")
        
        with gr.Row():
            with gr.Column():
                live_view = gr.Image(label="Latest Detection")
            with gr.Column():
                history = gr.Dataframe(
                    headers=["Time", "Label", "Score", "BBox"],
                    datatype=["str", "str", "str", "str"],
                    interactive=False
                )
        
        app.load(
            dashboard.get_detections,
            outputs=[live_view, history]
        )
    
    return app

if __name__ == "__main__":
    interface = create_interface()
    interface.launch()