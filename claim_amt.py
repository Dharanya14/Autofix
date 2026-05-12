from ultralytics import RTDETR

def get_claim_estimate(image_path):
    model = RTDETR(r"D:\autofix\autofix\model\best.pt")
    results = model.predict(source=image_path, save=True)

    cost_estimation = {
        "Bumper": (2151, 4480),
        "Bonnet": (3115, 5121),
        "Windshield": (3584, 5312),
        "Light": (2560, 4042),
        "Door": (4550, 7111),
        "Dickey": (4235, 7056),
    }

    detected_objects = [result.names[int(box.cls)] for result in results for box in result.boxes]
    total_avg = sum(
        (min_ + max_) // 2 
        for obj in detected_objects 
        if (min_ := cost_estimation.get(obj, (0, 0))[0]) 
        for max_ in [cost_estimation[obj][1]]
    )

    return total_avg, list(set(detected_objects))

