from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
import traceback
from claim_amt import get_claim_estimate
from heatmap import generate_heatmap
from damage_report import generate_report_and_save_pdf
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)


# Folder setup
UPLOAD_FOLDER = 'static/uploads'
HEATMAP_FOLDER = 'static/heatmaps'
REPORT_FOLDER = 'output'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(HEATMAP_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)

# ---------------- INDEX PAGE ----------------
@app.route("/")
def index():
    return render_template("index.html")

# ---------------- ABOUT PAGE (Claim Estimation) ----------------
@app.route("/about", methods=["GET"])
def about():
    return render_template("about.html")

@app.route("/process_claim", methods=["POST"])
def process_claim():
    try:
        if 'image' not in request.files or request.files['image'].filename == '':
            return jsonify({"error": "No image uploaded"})

        image = request.files['image']
        filename = secure_filename("claim_input.jpg")
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        image.save(image_path)

        print(f"[INFO] Image saved at {image_path}")

        from claim_amt import get_claim_estimate
        claim_amount, detected_parts = get_claim_estimate(image_path)

        print(f"[INFO] Claim: ₹{claim_amount}, Parts: {detected_parts}")

        return jsonify({
            "claim_amount": claim_amount,
            "parts": detected_parts
        })

    except Exception as e:
        print("[ERROR]", str(e))
        traceback.print_exc()
        return jsonify({"error": "Something went wrong while processing the image."})

# ---------------- SERVICES PAGE (Heatmap Generation) ----------------
@app.route("/service", methods=["GET", "POST"])
def service():
    if request.method == "POST":
        if 'image' not in request.files or request.files['image'].filename == "":
            return render_template("service.html", error="No image uploaded")

        image = request.files["image"]
        filename = secure_filename("heatmap_input.jpg")
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        image.save(image_path)

        heatmap_filename = generate_heatmap(image_path)
        heatmap_path = os.path.join("heatmaps", heatmap_filename)  # inside static/

        return render_template("service.html", heatmap_img=heatmap_path)

    return render_template("service.html", heatmap_img=None)

# ---------------- CONTACT PAGE (Report Generation) ----------------
@app.route("/contact", methods=["GET"])
def contact():
    try:
        report_text, pdf_path = generate_report_and_save_pdf()
        return render_template("contact.html", 
                               report=report_text, 
                               pdf_link=os.path.basename(pdf_path))
    except Exception as e:
        return render_template("contact.html", error=str(e))

# Serve PDF download
@app.route("/report/<filename>")
def report_file(filename):
    return send_from_directory(REPORT_FOLDER, filename)

# ---------------- Run the app ----------------
if __name__ == "__main__":
    app.run(debug=True)

