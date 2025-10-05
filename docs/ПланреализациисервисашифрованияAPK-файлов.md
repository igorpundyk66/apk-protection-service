# План реализации сервиса шифрования APK-файлов

## Обзор

Данный документ содержит детальный план реализации веб-сервиса для автоматической защиты Android-приложений (APK-файлов). План включает архитектурные решения, технические детали реализации, алгоритмы обработки и рекомендации по развертыванию.

## 1. Архитектура системы

Сервис состоит из трех основных компонентов, которые взаимодействуют друг с другом для обеспечения полного цикла обработки APK-файлов.

### 1.1 Frontend (Клиентская часть)

Frontend представляет собой веб-интерфейс, который обеспечивает взаимодействие пользователя с сервисом. Он реализован с использованием современных веб-технологий и включает следующие функции:

**Загрузка файлов**: Пользователь может загрузить APK-файл через drag-and-drop интерфейс или через стандартный диалог выбора файла. Frontend валидирует расширение файла и отображает имя выбранного файла.

**Отправка на обработку**: После выбора файла пользователь нажимает кнопку "Зашифровать и защитить APK", что инициирует отправку файла на backend через HTTP POST-запрос с использованием `multipart/form-data`.

**Индикация прогресса**: Во время обработки отображается progress bar с симулированным прогрессом (0-90% во время ожидания ответа, 100% после завершения).

**Скачивание результата**: После успешной обработки защищенный APK-файл автоматически скачивается на устройство пользователя с именем `protected_<original_name>.apk`.

**Обработка ошибок**: В случае ошибки отображается понятное сообщение об ошибке с описанием проблемы.

### 1.2 Backend (Серверная часть)

Backend реализован на Python с использованием фреймворка Flask и обеспечивает обработку APK-файлов. Основные компоненты включают:

**API Endpoint**: `POST /api/apk/upload` принимает APK-файл через `multipart/form-data` и возвращает защищенный APK-файл.

**Обработчик файлов**: Модуль для приема, валидации и сохранения загруженных файлов во временную директорию.

**Интеграция с Obfuscapk**: Модуль для вызова Obfuscapk с необходимыми параметрами и обработки результатов.

**Управление временными файлами**: Автоматическая очистка временных файлов после завершения обработки для предотвращения переполнения диска.

### 1.3 Obfuscapk (Инструмент обфускации)

Obfuscapk является внешним инструментом, который выполняет фактическую обработку APK-файлов. Он вызывается из backend через subprocess и применяет множество техник обфускации и шифрования.

## 2. Детальный алгоритм обработки APK

Процесс обработки APK-файла включает следующие этапы:

### Этап 1: Прием и валидация файла

Backend получает файл через POST-запрос и выполняет следующие проверки:

1. Проверка наличия поля `file` в запросе
2. Проверка, что файл не пустой
3. Проверка расширения файла (должно быть `.apk`)
4. Проверка размера файла (ограничение, например, 100 МБ)

Если валидация не пройдена, возвращается ошибка `400 Bad Request` с описанием проблемы.

### Этап 2: Сохранение во временную директорию

Загруженный файл сохраняется во временную директорию с уникальным идентификатором (UUID) для изоляции обработки каждого файла:

```
.tmp/apk_uploads/<uuid>.apk
```

Это предотвращает конфликты при одновременной обработке нескольких файлов.

### Этап 3: Применение методов защиты с Obfuscapk

Backend вызывает Obfuscapk через subprocess с следующими параметрами:

```bash
python3 /path/to/obfuscapk/cli.py \
  -o NewSignature \
  -o NewAlignment \
  -o Rebuild \
  -o ResStringEncryption \
  -o FieldRename \
  -o MethodRename \
  -o ClassRename \
  -o CallIndirection \
  -o ConstStringEncryption \
  -o ArithmeticBranch \
  -o Nop \
  -o Goto \
  -o RandomManifest \
  --keystore-file /path/to/debug.keystore \
  --keystore-password android \
  --key-alias androiddebugkey \
  --key-password android \
  -w /path/to/workdir \
  -d /path/to/output.apk \
  /path/to/input.apk
```

Obfuscapk выполняет следующие операции:

1. Декомпиляция APK с использованием apktool
2. Применение выбранных техник обфускации к Smali-коду и ресурсам
3. Рекомпиляция APK
4. Выравнивание APK с использованием zipalign
5. Подпись APK с использованием apksigner

### Этап 4: Проверка результата

После завершения работы Obfuscapk backend проверяет:

1. Код возврата subprocess (должен быть 0)
2. Наличие выходного файла
3. Размер выходного файла (не должен быть 0)

Если проверка не пройдена, возвращается ошибка `500 Internal Server Error` с описанием проблемы.

### Этап 5: Возврат защищенного APK

Защищенный APK-файл отправляется пользователю через `send_file()` с параметром `as_attachment=True`, что инициирует скачивание файла в браузере.

### Этап 6: Очистка временных файлов

После отправки файла или в случае ошибки backend удаляет:

1. Загруженный APK-файл
2. Рабочую директорию Obfuscapk
3. Выходной APK-файл (если он был создан)

Это предотвращает накопление временных файлов и переполнение диска.

## 3. Структура кода Backend

### 3.1 Главный файл приложения (src/main.py)

```python
from flask import Flask, render_template
from src.routes.apk_processing import apk_processing_bp

app = Flask(__name__, 
            static_folder=".tmp/apk_uploads", 
            template_folder="src/static")

# Регистрация Blueprint для обработки APK
app.register_blueprint(apk_processing_bp, url_prefix="/api/apk")

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
```

### 3.2 API Endpoint для обработки APK (src/routes/apk_processing.py)

```python
from flask import Blueprint, request, send_file, jsonify
import os
import subprocess
import shutil
import uuid

apk_processing_bp = Blueprint("apk_processing", __name__)

UPLOAD_FOLDER = ".tmp/apk_uploads"
PROCESSED_FOLDER = ".tmp/apk_processed"
KEYSTORE_PATH = ".tmp/debug.keystore"
KEYSTORE_PASS = "android"
KEY_ALIAS = "androiddebugkey"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Генерация debug keystore при первом запуске
if not os.path.exists(KEYSTORE_PATH):
    subprocess.run([
        "keytool", "-genkeypair",
        "-v", "-keystore", KEYSTORE_PATH,
        "-alias", KEY_ALIAS,
        "-keyalg", "RSA", "-keysize", "2048",
        "-validity", "10000",
        "-dname", "CN=Android Debug,O=Android,C=US",
        "-storepass", KEYSTORE_PASS,
        "-keypass", KEYSTORE_PASS
    ], check=True)

@apk_processing_bp.route("/upload", methods=["POST"])
def upload_apk():
    # Валидация запроса
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    
    if not file.filename.endswith(".apk"):
        return jsonify({"error": "Invalid file type, only .apk allowed"}), 400
    
    # Сохранение файла
    unique_id = str(uuid.uuid4())
    upload_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}.apk")
    file.save(upload_path)
    
    try:
        # Обработка APK
        processed_apk_path = process_apk(upload_path, unique_id)
        
        # Возврат защищенного APK
        return send_file(
            processed_apk_path, 
            as_attachment=True, 
            download_name=f"protected_{file.filename}"
        )
    except subprocess.CalledProcessError as e:
        return jsonify({
            "error": f"APK processing failed: {e.stderr.decode()}"
        }), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        # Очистка временных файлов
        cleanup_temp_files(unique_id, upload_path)

def process_apk(apk_path, unique_id):
    obfuscapk_dir = "/tmp/Obfuscapk"
    obfuscated_apk_path = os.path.join(
        PROCESSED_FOLDER, 
        f"obfuscated_{unique_id}.apk"
    )
    
    obfuscapk_command = [
        "python3", os.path.join(obfuscapk_dir, "src", "obfuscapk", "cli.py"),
        "-o", "NewSignature",
        "-o", "NewAlignment",
        "-o", "Rebuild",
        "-o", "ResStringEncryption",
        "-o", "FieldRename",
        "-o", "MethodRename",
        "-o", "ClassRename",
        "-o", "CallIndirection",
        "-o", "ConstStringEncryption",
        "-o", "ArithmeticBranch",
        "-o", "Nop",
        "-o", "Goto",
        "-o", "RandomManifest",
        "--keystore-file", KEYSTORE_PATH,
        "--keystore-password", KEYSTORE_PASS,
        "--key-alias", KEY_ALIAS,
        "--key-password", KEYSTORE_PASS,
        "-w", os.path.join(UPLOAD_FOLDER, unique_id + "_obfuscapk_workdir"),
        "-d", obfuscated_apk_path,
        apk_path
    ]
    
    subprocess.run(obfuscapk_command, check=True, capture_output=True)
    
    return obfuscated_apk_path

def cleanup_temp_files(unique_id, upload_path):
    # Удаление рабочей директории Obfuscapk
    shutil.rmtree(
        os.path.join(UPLOAD_FOLDER, unique_id + "_obfuscapk_workdir"), 
        ignore_errors=True
    )
    
    # Удаление загруженного файла
    if os.path.exists(upload_path):
        os.remove(upload_path)
    
    # Удаление обработанного файла
    processed_path = os.path.join(PROCESSED_FOLDER, f"obfuscated_{unique_id}.apk")
    if os.path.exists(processed_path):
        os.remove(processed_path)
```

## 4. Структура Frontend

Frontend реализован как single-page application (SPA) с использованием vanilla JavaScript. Основные компоненты:

### 4.1 HTML-структура

```html
<div class="container">
    <h1>🔐 APK Encryptor</h1>
    <p class="subtitle">Защитите ваше Android-приложение</p>
    
    <div class="upload-area" id="uploadArea">
        <div class="upload-icon">📱</div>
        <div class="upload-text">Перетащите APK-файл сюда</div>
    </div>
    
    <input type="file" id="fileInput" accept=".apk">
    
    <div class="selected-file" id="selectedFile">
        <strong>Выбранный файл:</strong> <span id="fileName"></span>
    </div>
    
    <button class="btn btn-primary" id="uploadBtn">
        Зашифровать и защитить APK
    </button>
    
    <div class="progress-container" id="progressContainer">
        <div class="progress-bar">
            <div class="progress-fill" id="progressFill">0%</div>
        </div>
    </div>
    
    <div class="status-message" id="statusMessage"></div>
</div>
```

### 4.2 JavaScript-логика

```javascript
uploadBtn.addEventListener('click', async () => {
    if (!selectedApkFile) return;
    
    uploadBtn.disabled = true;
    progressContainer.classList.add('show');
    showStatus('Обработка APK...', 'info');
    
    const formData = new FormData();
    formData.append('file', selectedApkFile);
    
    try {
        // Симуляция прогресса
        simulateProgress();
        
        // Отправка файла на backend
        const response = await fetch('/api/apk/upload', {
            method: 'POST',
            body: formData
        });
        
        updateProgress(100);
        
        if (response.ok) {
            // Скачивание защищенного APK
            const blob = await response.blob();
            downloadFile(blob, `protected_${selectedApkFile.name}`);
            showStatus('✅ APK успешно защищен!', 'success');
            resetForm();
        } else {
            const error = await response.json();
            showStatus(`❌ Ошибка: ${error.error}`, 'error');
        }
    } catch (error) {
        showStatus(`❌ Ошибка сети: ${error.message}`, 'error');
    } finally {
        uploadBtn.disabled = false;
    }
});
```

## 5. Развертывание

### 5.1 Локальное развертывание

Для локального тестирования выполните следующие шаги:

1. Клонируйте репозиторий Obfuscapk:
   ```bash
   git clone https://github.com/ClaudiuGeorgiu/Obfuscapk.git /tmp/Obfuscapk
   ```

2. Установите зависимости backend:
   ```bash
   cd apk_encryptor_backend
   python3 -m venv venv
   source venv/bin/activate
   pip install flask lxml beautifulsoup4 tqdm
   ```

3. Установите Android SDK Build Tools:
   ```bash
   sudo apt update
   sudo apt install -y openjdk-17-jdk android-sdk
   ```

4. Запустите Flask-приложение:
   ```bash
   python src/main.py
   ```

5. Откройте браузер и перейдите по адресу `http://localhost:5000`

### 5.2 Production-развертывание

Для production-развертывания рекомендуется использовать следующую конфигурацию:

**Web-сервер**: Nginx в качестве reverse proxy для Flask-приложения

**WSGI-сервер**: Gunicorn или uWSGI для запуска Flask-приложения

**Контейнеризация**: Docker для изоляции окружения и упрощения развертывания

**Хостинг**: AWS EC2, Google Cloud Compute Engine, DigitalOcean или аналогичные

**HTTPS**: Let's Encrypt для бесплатных SSL-сертификатов

**Мониторинг**: Prometheus + Grafana для мониторинга производительности

## 6. Текущие проблемы и решения

### Проблема 1: Ошибка 405 Method Not Allowed

**Описание**: При отправке POST-запроса на `/api/apk/upload` возникает ошибка 405.

**Возможные причины**:
1. Blueprint не зарегистрирован корректно в `main.py`
2. Конфликт маршрутов или неправильный `url_prefix`
3. Проблема с обработкой `multipart/form-data` в Flask
4. Кэширование старой версии кода в debug-режиме

**Решения для проверки**:
1. Убедиться, что Blueprint зарегистрирован с правильным `url_prefix`
2. Проверить, что декоратор `@route` содержит `methods=["POST"]`
3. Добавить логирование для отладки зарегистрированных маршрутов
4. Полностью перезапустить Flask-приложение (убить все процессы)
5. Попробовать упростить endpoint для тестирования (без обработки файлов)

### Проблема 2: Длительное время обработки

**Описание**: Обработка APK с Obfuscapk может занимать несколько минут.

**Решение**: 
1. Реализовать асинхронную обработку с использованием Celery + Redis
2. Добавить WebSocket для real-time обновления прогресса
3. Оптимизировать выбор техник обфускации (отключить самые медленные)

### Проблема 3: Увеличение размера APK

**Описание**: Некоторые техники обфускации увеличивают размер APK.

**Решение**:
1. Использовать zipalign для оптимизации размера
2. Предоставить пользователю выбор техник обфускации
3. Добавить пост-обработку для сжатия ресурсов

## 7. Дальнейшее развитие

### 7.1 Краткосрочные улучшения

1. Исправление ошибки 405 и завершение базовой функциональности
2. Добавление тестов для API endpoints
3. Улучшение обработки ошибок и логирования
4. Оптимизация производительности обработки

### 7.2 Среднесрочные улучшения

1. Реализация асинхронной обработки с очередью задач
2. Добавление аутентификации и авторизации пользователей
3. Сохранение истории обработанных APK
4. Добавление настроек выбора техник обфускации

### 7.3 Долгосрочные улучшения

1. Поддержка Android App Bundle (AAB) файлов
2. Интеграция с CI/CD pipeline (GitHub Actions, GitLab CI)
3. REST API для автоматизации защиты APK
4. Аналитика и отчеты о примененных методах защиты
5. Поддержка пользовательских keystore для подписи

## Заключение

Данный план реализации предоставляет детальное руководство по созданию сервиса защиты APK-файлов. Основная архитектура и алгоритмы обработки определены, большая часть кода реализована. Основная проблема заключается в отладке ошибки 405 при обработке POST-запросов, после чего сервис будет готов к тестированию и развертыванию.
