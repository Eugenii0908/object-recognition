from flask import Flask, request, render_template, send_from_directory
from ultralytics import YOLO
import os
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = 'C:/Users/User/Desktop/yolo_webapp/uploads'
RESULT_FOLDER = 'C:/Users/User/Desktop/yolo_webapp/results'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

# Загрузка обученной модели
model = YOLO('F:/Загрузки/epoch58.pt')  # Замените на свой путь

@app.route('/', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        file = request.files['image']
        if file:
            filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            results = model.predict(source=filepath, conf<0.19, save=True, project=RESULT_FOLDER, name='predict', exist_ok=True)

            result_image_rel_path = f"results/predict/{filename}"
            return render_template('index.html', result_image=result_image_rel_path)
    return render_template('index.html')

@app.route('/results/<path:filename>')
def serve_results(filename):
    return send_from_directory('results', filename)

if __name__ == '__main__':
    app.run(debug=True)

