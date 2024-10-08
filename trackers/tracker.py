from ultralytics import YOLO
import pandas as pd
import supervision as sv
import pickle
import os
import sys
import cv2
import numpy as np
sys.path.append('../')
from utils import get_bbox_width, get_center_of_bbox

class Tracker:
    def __init__(self, model_path):
        self.model = YOLO(model_path)
        self.tracker = sv.ByteTrack()


#extracting frames and running our fine tuned YOLO model on them
    def detect_frames(self,frames):
        batch_size = 20
        detections = []
        for i in range(0, len(frames), batch_size):
            detections_batch = self.model.predict(frames[i:(i+batch_size)], conf = 0.1)
            detections += detections_batch
        return detections

#this function returns all the tracked items in a single dictionary
#this tracks dictionary will become a useful reference in accessing bounding boxes and track ids
    def get_object_tracks(self,frames,read_from_stubs = False, stub_pathway = None):

        if read_from_stubs and stub_pathway is not None and os.path.exists(stub_pathway):
            with open(stub_pathway, 'rb') as f:
                tracks = pickle.load(f)
            return tracks


        detections = self.detect_frames(frames)

        tracks = {
            "players":[],
            "referees":[],
            "ball":[]
        }
        #creating a class variable that holds a dictionary containing class and class_id
        for frame_num, detection in enumerate(detections):
            cls_names = detection.names
            cls_names_inv = {v:k for k,v in cls_names.items()}

            #convert to supervision Detection format
            detection_sv = sv.Detections.from_ultralytics(detection)

            #converting keeper to player to avoid unnecessary confusion
            for object_ind, class_id in enumerate(detection_sv.class_id):
                if cls_names[class_id] == "goalkeeper":
                    detection_sv.class_id[object_ind] = cls_names_inv["player"]              
            
            #tracking
            detection_with_tracks = self.tracker.update_with_detections(detection_sv)

            tracks["players"].append({})
            tracks["referees"].append({})
            tracks["ball"].append({})

            for frame_detection in detection_with_tracks:
                bbox = frame_detection[0].tolist()
                cls_id = frame_detection[3]
                track_id = frame_detection[4]

                if cls_id == cls_names_inv['player']:
                    tracks["players"][frame_num][track_id] = {"bbox":bbox}
                if cls_id == cls_names_inv['referee']:
                    tracks["referees"][frame_num][track_id] = {"bbox": bbox}

            for fname_detection in detection_sv:
                bbox = frame_detection[0].tolist()
                cls_id = fname_detection[3]

                if cls_id == cls_names_inv["ball"]:
                    tracks["ball"][frame_num][1] = {"bbox":bbox}

        if stub_pathway is not None:
            with open(stub_pathway, 'wb') as f:
                pickle.dump(tracks,f)

        return tracks
#contrary to the name it does more than draw an ellipse

    def draw_ellipse(self, frame, bbox, color, track_id = None):
        y2 = int(bbox[3])

        x_centre, _= get_center_of_bbox(bbox)
        width = get_bbox_width(bbox)

        cv2.ellipse(
            frame,
            center = (x_centre, y2),
            axes = (int(width), int(0.35*width)),
            angle = 0.0,
            startAngle=-45,
            endAngle=235,
            color=color,
            thickness= 2,
            lineType= cv2.LINE_4
        )

        rectangle_width = 40
        rectangle_height = 20
        x1_rect = x_centre - rectangle_width//2
        x2_rect = x_centre + rectangle_width//2
        y1_rect = (y2 - rectangle_height//2)+15
        y2_rect = (y2 + rectangle_height//2)+15

        if track_id is not None:
            cv2.rectangle(frame,
                          (int(x1_rect), int(y1_rect)),
                           (int(x2_rect), int(y2_rect)),
                           color,
                           cv2.FILLED)
            
            x1_text = x1_rect + 12
            if track_id>99:
                x1_text -= 10

            cv2.putText(
                frame, 
                f"{track_id}",
                (int(x1_rect), int(y1_rect+15)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0,0,0),
                2

            )
        return frame
    
    def draw_triangle(self,frame,bbox,color):
        y= int(bbox[1])
        x,_ = get_center_of_bbox(bbox)

        triangle_points = np.array([
            [x,y],
            [x-10,y-20],
            [x+10,y-20],
        ])
        cv2.drawContours(frame, [triangle_points],0,color, cv2.FILLED)
        cv2.drawContours(frame, [triangle_points],0,(0,0,0), 2)

        return frame

         


#gets video frames and annotates the ball tracker and player trackes
    def draw_annotations(self, video_frames, tracks):
        output_video_frames  =[]
        for frame_num, frame in enumerate(video_frames):
            frame = frame.copy()

            player_dict = tracks["players"][frame_num]
            ball_dict = tracks["ball"][frame_num]
            referee_dict = tracks["referees"][frame_num]


            for track_id, player in player_dict.items():
                color = player.get("team_color", (0,0,255))
                frame = self.draw_ellipse(frame, player["bbox"], color, track_id)

                

            for _, referee in referee_dict.items():
                frame = self.draw_ellipse(frame, referee["bbox"], (0,255,255))
            
            for track_id, ball in ball_dict.items():
                frame = self.draw_triangle(frame, ball["bbox"], (0,255,0))

            output_video_frames.append(frame)

        return output_video_frames