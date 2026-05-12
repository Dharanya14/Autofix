from ultralytics import RTDETR
model = RTDETR(r"E:\project-final\autofix\model\best.pt")
results = model.predict(source=r'E:\project-final\autofix\predict\car_1.jpg', save=True)