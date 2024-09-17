from ultralytics import YOLO

model = YOLO('models_robo/best.pt')

results = model.predict('08fd33_4.mp4', save = True)