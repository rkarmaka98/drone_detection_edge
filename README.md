# OpenMV Drone Detection System

## Overview
A complete real-time drone detection system using OpenMV camera with local processing and MQTT integration. This solution processes camera frames, detects objects, and forwards results to a dashboard - all running on localhost.

## Features
- Real-time object detection using OpenMV's machine learning
- Three communication methods: Serial, TCP, and Named Pipes
- Live monitoring dashboard with detection visualization
- MQTT integration for IoT connectivity
- Local operation without internet requirement
- Configurable detection parameters

## Installation

### Prerequisites
- OpenMV H7 camera
- OpenMV IDE
- Python 3.8+
- Mosquitto MQTT broker (for MQTT option)

```bash
# Clone the repository
git clone https://github.com/rkarmaka98/openmv-drone-detection.git
cd openmv-drone-detection

# Install Python dependencies
pip install -r requirements.txt
```
