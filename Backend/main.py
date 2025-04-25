#http://localhost:8000/docs


from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse  
from contextlib import asynccontextmanager
from ultralytics import YOLO
from PIL import Image
import io
import os
import uuid

# Папка для хранения размеченных изображений
UPLOAD_FOLDER = "annotated_images"
# Создаем папку, если она не существует
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
BASE_URL = "http://localhost:8000"  

# Асинхронный менеджер контекста для управления загрузкой и выгрузкой модели
# Загружает модель при старте приложения, освобождает память при завершении
@asynccontextmanager
async def lifespan(app: FastAPI):
    global model
    try:
        # Загрузка предобученной YOLO модели из файла
        model = YOLO('epoch58.pt')
        print("Model loaded successfully")
    except Exception as e:
        # В случае ошибки выводим сообщение и прерываем выполнение
        print(f"Error loading model: {e}")
        raise
    yield # Точка, где приложение работает
    model = None # Очистка модели при завершении

# Создание экземпляра FastAPI приложения с указанием lifespan менеджера
app = FastAPI(
    lifespan=lifespan, # Подключаем менеджер жизненного цикла
    title="YOLO Object Detection API", # Название API
    # Описание
    description="API возвращает JSON с данными объектов и ссылкой на размеченное изображение"
)

# Эндпоинт для обработки изображений
@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        # Генерация уникального имени файла
        file_id = str(uuid.uuid4())
        output_filename = f"{file_id}.jpg"
        output_path = os.path.join(UPLOAD_FOLDER, output_filename)
        
        # Чтение содержимого загруженного файла
        contents = await file.read()
        # Создание объекта изображения из бинарных данных
        image = Image.open(io.BytesIO(contents))
        # Выполнение предсказания на загруженном изображении
        results = model(image)
        
        # Сохранение размеченного изображения
        results[0].save(output_path)
        
        # Формирование JSON ответа
        predictions = [] # Список для хранения результатов
        for box in results[0].boxes: # Перебор всех обнаруженных объектов
            predictions.append({
                "class": model.names[int(box.cls)],
                "confidence": float(box.conf),
                "bbox": box.xyxy[0].tolist()
            })
        
        # Возвращаем результаты
        return {
            "predictions": predictions,
            "annotated_image_url": f"{BASE_URL}/annotated/{file_id}"
        }
        
    except Exception as e:
        # Удаляем файл в случае ошибки
        if 'output_path' in locals() and os.path.exists(output_path):
            os.remove(output_path)
        # В случае любой ошибки возвращаем HTTP 500 с описанием ошибки
        raise HTTPException(500, str(e))

# Эндпоинт для получения размеченного изображения
@app.get("/annotated/{file_id}")
async def get_annotated_image(file_id: str):
    # Формируем полный путь к файлу изображения
    file_path = os.path.join(UPLOAD_FOLDER, f"{file_id}.jpg")
    # Проверяем существование файла
    if not os.path.exists(file_path):
        # Если файл не найден - возвращаем 404 ошибку
        raise HTTPException(404, "Annotated image not found")
    
    # Возвращаем файл изображения с настройками
    return FileResponse(
        file_path, # Путь к файлу на сервере
        media_type="image/jpeg",
        filename="annotated_image.jpg" # Имя файла
    )

# Точка входа при запуске скрипта 
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0", # Приложение доступно с любого IP в сети
        port=8000, # Порт, на котором будет работать сервер
        reload=True # Автоматическая перезагрузка при изменении кода
    )