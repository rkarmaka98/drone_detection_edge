# OpenMV Drone Detection Dashboard

![image](https://github.com/user-attachments/assets/3e03d7bb-8f38-4311-9b2c-3570dbeeeef1)
*A Gradio-based dashboard for visualizing drone detection data from OpenMV*

## 📌 Overview

This project provides a real-time monitoring system for drone detection using:
- **OpenMV Cam** for onboard object detection (FOMO model)
- **CSV logging** for persistent data storage
- **Interactive Gradio dashboard** for data visualization

## 🛠️ Features

- **Four interactive plots**:
  - Confidence scores over time
  - Position heatmap (OpenMV coordinate system)
  - Detection frequency timeline
  - Confidence distribution histogram
- **Dynamic filtering**:
  - Adjustable confidence threshold
  - Class-based filtering
- **Data management**:
  - CSV auto-reloading
  - Raw data inspection

## ⚙️ Hardware Requirements

- OpenMV Cam (H7 recommended)
- MicroSD card (for CSV storage)
- USB cable/Wi-Fi module (for data transfer)

## 🚀 Installation

1. ### Clone the repository:
   ```bash
   git clone https://github.com/rkarmaka98/drone_detection_edge.git
   cd drone_detection_edge
   ```
2. ### Architecture
```mermaid
graph LR
    A[OpenMV Camera] -->|Writes CSV| B[SD Card]
    B -->|Read by| C[Gradio Dashboard]
    C --> D[Interactive Visualizations]
```
3. ### Usage
* Run the OpenMV detection script
* Start the dashboard:
```bash
python dashboard.py
```
* Access the dashboard at http://localhost:7860
