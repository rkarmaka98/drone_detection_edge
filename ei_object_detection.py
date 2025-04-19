# Edge Impulse - OpenMV CSV Logger
import sensor, image, time, ml, math
from ml.utils import NMS
import uos

# Camera setup
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time=2000)

# Model setup
model = ml.Model("trained")
min_confidence = 0.4
threshold_list = [(math.ceil(min_confidence * 255), 255)]

# CSV file setup
CSV_FILENAME = "detections.csv"
HEADER = "timestamp,class,x,y,score,width,height\n"

# Initialize CSV file if it doesn't exist
with open(CSV_FILENAME, "w") as f:
        f.write(HEADER)

def fomo_post_process(model, inputs, outputs):
    n, oh, ow, oc = model.output_shape[0]
    nms = NMS(ow, oh, inputs[0].roi)
    for i in range(oc):
        img = image.Image(outputs[0][0, :, :, i] * 255)
        blobs = img.find_blobs(threshold_list, x_stride=1, area_threshold=1, pixels_threshold=1)
        for b in blobs:
            rect = b.rect()
            x, y, w, h = rect
            score = img.get_statistics(thresholds=threshold_list, roi=rect).l_mean() / 255.0
            nms.add_bounding_box(x, y, x + w, y + h, score, i)
    return nms.get_bounding_boxes()

def log_detection(timestamp, class_name, x, y, score, w, h):
    with open(CSV_FILENAME, "a") as f:
        f.write(f"{timestamp},{class_name},{x},{y},{score},{w},{h}\n")
        print("Adding entry!!")

clock = time.clock()
while True:
    clock.tick()
    img = sensor.snapshot()
    timestamp = time.ticks_ms()
    
    for i, detection_list in enumerate(model.predict([img], callback=fomo_post_process)):
        if i == 0 or not detection_list:
            continue
        
        class_name = model.labels[i].split()[0]
        print(class_name)
        for (x, y, w, h), score in detection_list:
            center_x = math.floor(x + (w / 2))
            center_y = math.floor(y + (h / 2))
            log_detection(timestamp, class_name, center_x, center_y, score, w, h)
            
            # Optional: Draw on image
            img.draw_rectangle(x, y, w, h, color=(255, 0, 0), thickness=2)
            label = f"{class_name}: {score:.2f}"
            img.draw_string(x, y - 10, label, color=(255, 0, 0), scale=1)
    