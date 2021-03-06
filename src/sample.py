#================================================================
#   Original code   : https://github.com/pythonlessons/TensorFlow-2.x-YOLOv3#
#================================================================
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '0'
import cv2
import numpy as np
import tensorflow as tf
from yolov3.utils import Load_Yolo_model, image_preprocess, postprocess_boxes, nms, draw_bbox, read_class_names
from yolov3.configs import *
import time

from deep_sort import nn_matching
from deep_sort.detection import Detection
from deep_sort.tracker import Tracker
from deep_sort import generate_detections as gdet


yolo = Load_Yolo_model()

# Definition of the parameters
input_size= YOLO_INPUT_SIZE # default=416
CLASSES=YOLO_COCO_CLASSES
score_threshold = 0.3
iou_threshold = 0.45 # default=0.1
rectangle_colors = (255,0,0)
Track_only = ['person']
max_cosine_distance = 0.7
nn_budget = None

#initialize deep sort object
model_filename = 'model_data/mars-small128.pb'
encoder = gdet.create_box_encoder(model_filename, batch_size=1)
metric = nn_matching.NearestNeighborDistanceMetric("cosine", max_cosine_distance, nn_budget)
tracker = Tracker(metric)

times, times_2 = [], []

NUM_CLASS = read_class_names(CLASSES)
key_list = list(NUM_CLASS.keys()) 
val_list = list(NUM_CLASS.values())

# 動画ファイルを読み込む場合は以下を使う
cap = cv2.VideoCapture('sample.mp4')

# Gstreamerから映像を取得する場合は以下を使う
# elements = [
#     'autovideosrc',
#     'videoconvert',
#     'appsink',
# ]
# src = ' ! '.join(elements)
# cap = cv2.VideoCapture(src)

try:
    while True:
        _, frame = cap.read()
        if frame is None: break

        original_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        original_frame = cv2.cvtColor(original_frame, cv2.COLOR_BGR2RGB)

        image_data = image_preprocess(np.copy(original_frame), [input_size, input_size])
        image_data = image_data[np.newaxis, ...].astype(np.float32)

        t1 = time.time()
        pred_bbox = yolo.predict(image_data)
        
        pred_bbox = [tf.reshape(x, (-1, tf.shape(x)[-1])) for x in pred_bbox]
        pred_bbox = tf.concat(pred_bbox, axis=0)

        bboxes = postprocess_boxes(pred_bbox, original_frame, input_size, score_threshold)
        bboxes = nms(bboxes, iou_threshold, method='nms')

        # extract bboxes to boxes (x, y, width, height), scores and names
        boxes, scores, names = [], [], []
        for bbox in bboxes:
            if len(Track_only) !=0 and NUM_CLASS[int(bbox[5])] in Track_only or len(Track_only) == 0:
                boxes.append([bbox[0].astype(int), bbox[1].astype(int), bbox[2].astype(int)-bbox[0].astype(int), bbox[3].astype(int)-bbox[1].astype(int)])
                scores.append(bbox[4])
                names.append(NUM_CLASS[int(bbox[5])])

        # Obtain all the detections for the given frame.
        boxes = np.array(boxes) 
        names = np.array(names)
        scores = np.array(scores)
        features = np.array(encoder(original_frame, boxes))
        detections = [Detection(bbox, score, class_name, feature) for bbox, score, class_name, feature in zip(boxes, scores, names, features)]

        # Pass detections to the deepsort object and obtain the track information.
        tracker.predict()
        tracker.update(detections)

        # Obtain info from the tracks
        tracked_bboxes = []
        for track in tracker.tracks:
            if not track.is_confirmed() or track.time_since_update > 5:
                continue 
            bbox = track.to_tlbr() # Get the corrected/predicted bounding box
            class_name = track.get_class() #Get the class name of particular object
            tracking_id = track.track_id # Get the ID for the particular track
            index = key_list[val_list.index(class_name)] # Get predicted object index by object name
            tracked_bboxes.append(bbox.tolist() + [tracking_id, index]) # Structure data, that we could use it with our draw_bbox function

        # draw detection on frame
        image = draw_bbox(original_frame, tracked_bboxes, CLASSES=CLASSES, tracking=True)

        t3 = time.time()
        times.append(t3-t1)
        sec = sum(times[-20:])/len(times[-20:])
        fps  = 1.0 / sec
        
        image = cv2.putText(image, "Time: {:.1f} FPS".format(fps), (0, 30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255), 2)
        print("Time: {:.2f}ms, total FPS: {:.1f}".format(sec * 1000, fps))
        cv2.imshow('output', image)
        
        if cv2.waitKey(25) & 0xFF == ord("q"):
            raise KeyboardInterrupt

except KeyboardInterrupt:
    cap.release()
    cv2.destroyAllWindows()