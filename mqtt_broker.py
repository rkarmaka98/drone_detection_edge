#!/usr/bin/env python3
import socket
import json
import paho.mqtt.client as mqtt

class NetworkForwarder:
    def __init__(self):
        self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "network_forwarder")
        self.mqtt_client.connect("localhost", 1883)
        self.mqtt_client.loop_start()
        
    def connect_to_openmv(self, host='192.168.1.100', port=8080):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        print(f"Connected to OpenMV at {host}:{port}")
        
    def forward_messages(self):
        buffer = ""
        while True:
            data = self.sock.recv(4096).decode('utf-8')
            if not data:
                print("Connection lost")
                break
                
            buffer += data
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                try:
                    payload = json.loads(line)
                    self.mqtt_client.publish("openmv/detections", line)
                except json.JSONDecodeError:
                    print("Invalid JSON:", line)

    def run(self):
        try:
            self.connect_to_openmv()
            self.forward_messages()
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            self.sock.close()
            self.mqtt_client.disconnect()

if __name__ == "__main__":
    forwarder = NetworkForwarder()
    forwarder.run()