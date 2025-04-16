import sensor, image, time, ml, math, network, usocket, ujson
from ml.utils import NMS

# Network Configuration with Error Handling
def setup_network():
    # Try LAN first, fall back to WiFi
    interfaces = [
        ('Ethernet', network.LAN()), 
        ('WiFi', network.WLAN(network.STA_IF))
    ]
    
    for name, net in interfaces:
        try:
            net.active(True)
            if name == 'Ethernet':
                # Manual config for LAN (adjust for your network)
                net.ifconfig(('192.168.1.100', '255.255.255.0', '192.168.1.1', '8.8.8.8'))
            else:
                # WiFi connection
                net.connect('your_SSID', 'your_password')
                for _ in range(10):  # Wait up to 10 seconds
                    if net.isconnected():
                        break
                    time.sleep(1)
            
            if net.isconnected():
                print(f"{name} connected! IP:", net.ifconfig()[0])
                return net
        except Exception as e:
            print(f"{name} failed:", e)
    
    raise Exception("All network interfaces failed")

# Initialize Network
try:
    NETWORK_IF = setup_network()
except Exception as e:
    print("Network init failed:", e)
    raise

# TCP Server Setup
server_socket = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
server_socket.setsockopt(usocket.SOL_SOCKET, usocket.SO_REUSEADDR, 1)
server_socket.bind(('0.0.0.0', 8080))
server_socket.listen(1)
print("TCP Server Started on port 8080")

# Model Configuration
model = ml.Model("trained")
min_confidence = 0.4
frame_interval = 100  # ms

def fomo_post_process(model, inputs, outputs):
    n, oh, ow, oc = model.output_shape[0]
    nms = NMS(ow, oh, inputs[0].roi)
    for i in range(oc):
        img = image.Image(outputs[0][0, :, :, i] * 255)
        blobs = img.find_blobs([(math.ceil(min_confidence*255), 255)],
                             x_stride=1, area_threshold=1, pixels_threshold=1)
        for b in blobs:
            rect = b.rect()
            score = img.get_statistics(roi=rect).l_mean()/255.0
            if score >= min_confidence:
                nms.add_bounding_box(rect[0], rect[1], rect[0]+rect[2], rect[1]+rect[3], score, i)
    return nms.get_bounding_boxes()

def handle_client(client_socket):
    last_frame = time.ticks_ms()
    while True:
        current_time = time.ticks_ms()
        if time.ticks_diff(current_time, last_frame) >= frame_interval:
            img = sensor.snapshot()
            detections = model.predict([img], callback=fomo_post_process)
            
            for i, detection_list in enumerate(detections):
                if i == 0 or not detection_list:
                    continue
                    
                for (x, y, w, h), score in detection_list:
                    if score >= min_confidence:
                        img.draw_rectangle(x, y, w, h, color=(255,0,0))
                        payload = {
                            "timestamp": time.localtime(),
                            "label": model.labels[i],
                            "score": score,
                            "bbox": (x,y,w,h),
                            "image": img.compress(quality=70).bytearray().hex()
                        }
                        try:
                            client_socket.write(ujson.dumps(payload) + "\n")
                        except:
                            return  # Client disconnected
            
            last_frame = current_time

# Camera Setup
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time=2000)

# Main Loop
while True:
    try:
        client, addr = server_socket.accept()
        print("Client connected:", addr)
        handle_client(client)
    except Exception as e:
        print("Error:", e)
    finally:
        client.close()