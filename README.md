# yolo_human_tracker
Sample program to track humans using Yolo v3.
[Original](https://github.com/pythonlessons/TensorFlow-2.x-YOLOv3#)

# Install
```
git clone https://github.com/social-robotics-lab/yolo_human_tracker.git
cd yolo_human_tracker
wget -P src/model_data https://pjreddie.com/media/files/yolov3.weights
docker build -t yolo_human_tracker .
```

# Run
```
docker run -it --name yolo_human_tracker --mount type=bind,source="$(pwd)"/src,target=/tmp --rm yolo_human_tracker /bin/bash
python sample.py
```