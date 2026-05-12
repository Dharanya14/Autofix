from ultralytics import RTDETR
from google.generativeai import configure, GenerativeModel
from fpdf import FPDF
import os

def generate_report_and_save_pdf():
    model = RTDETR(r"E:\project-final\autofix\model\best.pt")
    image_path = r'E:\project-final\autofix\predict\car_1.jpg'
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
    parts = set(detected_objects)

    # Gemini API - Key placed directly here
    api_key = "AIzaSyAWH3ml0KOLbFA3JnaWUejxzInEzAGfAfU"
    configure(api_key=api_key)
    gemini = GenerativeModel("gemini-1.5-flash")
    
    prompt = f"""Generate a car damage assessment report. 
    Estimated cost: Rs.{total_avg}, 
    Damaged parts: {', '.join(parts) if parts else 'No significant damage detected'}.
    
    Include sections:
    - Estimated Cost
    - Damaged Parts
    - Analysis
    - Justification"""

    response = gemini.generate_content([prompt])
    report_content = response.text

    # Save PDF
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    pdf_path = os.path.join(output_dir, "damage_assessment_report.pdf")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, report_content)
    pdf.output(pdf_path)
    
    return report_content, pdf_path
