// Смена фоновых изображений
const backgrounds = document.querySelectorAll('.ship-bg');
let currentBg = 0;

setInterval(() => {
    backgrounds[currentBg].classList.remove('active');
    currentBg = (currentBg + 1) % backgrounds.length;
    backgrounds[currentBg].classList.add('active');
}, 5000);

// Обработка выбора файла
document.getElementById('fileInput').addEventListener('change', function(e) {
    const fileName = e.target.files[0] ? e.target.files[0].name : 'Выберите файл изображения';
    document.getElementById('fileName').textContent = fileName;
});

// Показать результат в полноэкранном режиме
function showFullscreenResult(data) {
    const fsContainer = document.createElement('div');
    fsContainer.className = 'fullscreen-view';
    
    fsContainer.innerHTML = `
        <div class="hero-section">
            <img src="images/1.jpg" class="ship-bg active" alt="Ship background 1">
            <img src="images/2.jpg" class="ship-bg" alt="Ship background 2">
            <img src="images/3.jpg" class="ship-bg" alt="Ship background 3">
            <img src="images/4.jpg" class="ship-bg" alt="Ship background 4">

            <div class="container d-flex justify-content-center align-items-center" style="min-height: 100vh;">
                <div class="p-4 rounded-4" style="background: white; max-width: 700px; width: 100%;">
                    <button class="btn btn-secondary mb-3" onclick="this.closest('.fullscreen-view').remove()">← Назад к загрузке</button>
                    <div class="text-center">
                        <h3 class="mb-4" style="color: #0d1b2a;">Результат анализа</h3>
                        <img src="${data.annotated_image_url}" alt="Результат обработки" class="img-fluid mb-4" style="border-radius: 10px;">
                        <div class="result-details">
                            <div class="alert ${data.predictions.length > 0 ? 'alert-success' : 'alert-warning'} mb-4">
                                <strong>Обнаружено объектов:</strong> ${data.predictions.length}
                            </div>
                            <a href="${data.annotated_image_url}" download="annotated_image.jpg" class="btn btn-primary btn-lg mt-3">
                                Скачать размеченное изображение
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(fsContainer);

    // Анимация фона в полноэкранном режиме
    const newBackgrounds = fsContainer.querySelectorAll('.ship-bg');
    let newCurrentBg = 0;
    setInterval(() => {
        newBackgrounds[newCurrentBg].classList.remove('active');
        newCurrentBg = (newCurrentBg + 1) % newBackgrounds.length;
        newBackgrounds[newCurrentBg].classList.add('active');
    }, 5000);
}

// Обработка отправки формы
document.getElementById('uploadForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    const fileInput = document.getElementById('fileInput');
    if (!fileInput.files[0]) {
        alert('Пожалуйста, выберите файл изображения');
        return;
    }

    const spinner = document.getElementById('spinner');
    const buttonText = document.getElementById('buttonText');

    // Показываем индикатор загрузки
    spinner.classList.remove('d-none');
    buttonText.textContent = 'Обработка...';

    try {
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        // Отправляем запрос к API
        const response = await fetch('http://localhost:8000/predict', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`Ошибка сервера: ${response.status}`);
        }

        const data = await response.json();
        showFullscreenResult(data);

    } catch (error) {
        console.error('Ошибка при обработке изображения:', error);
        alert(`Произошла ошибка: ${error.message}`);
    } finally {
        // Восстанавливаем кнопку
        spinner.classList.add('d-none');
        buttonText.textContent = 'Загрузить и обработать';
    }
});
