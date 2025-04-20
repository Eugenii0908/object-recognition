import sys
import os

# ✅ Добавляем путь к локальной копии Ultralytics до любого импорта
sys.path.insert(0, os.path.abspath('./yolov11-ultralytics'))

from ultralytics import YOLO

# Пути к модели и изображению
model_path = r'models\best.pt'
image_path = r'test_img\testimage9.png'

# Проверка наличия файлов
assert os.path.exists(model_path), f'❌ Модель не найдена: {model_path}'
assert os.path.exists(image_path), f'❌ Изображение не найдено: {image_path}'

# Загрузка модели
model = YOLO(model_path)

# Предсказание
results = model.predict(
    source=image_path,
    imgsz=640,
    conf=0.2,
    save=True
)

print(f"✅ Предсказание завершено! Результат сохранён в: {results[0].save_dir}")
