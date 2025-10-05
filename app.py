"""
Главное Flask приложение для сервиса защиты APK
"""
from flask import Flask, send_from_directory
from config import Config
import logging
from pathlib import Path

# Создание Flask приложения
app = Flask(__name__, 
            static_folder='frontend',
            static_url_path='')
app.config.from_object(Config)

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Импорт и регистрация роутов
from api.routes import api_bp
app.register_blueprint(api_bp, url_prefix='/api')

@app.route('/')
def index():
    """Главная страница"""
    return send_from_directory('frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Обслуживание статических файлов"""
    return send_from_directory('frontend', path)

@app.errorhandler(413)
def request_entity_too_large(error):
    """Обработка ошибки слишком большого файла"""
    return {"error": "Файл слишком большой. Максимальный размер: 150 МБ"}, 413

@app.errorhandler(404)
def not_found(error):
    """Обработка 404 ошибки"""
    return {"error": "Ресурс не найден"}, 404

@app.errorhandler(500)
def internal_error(error):
    """Обработка внутренней ошибки сервера"""
    logger.error(f"Internal server error: {error}")
    return {"error": "Внутренняя ошибка сервера"}, 500

if __name__ == '__main__':
    logger.info("Запуск APK Protection Service...")
    logger.info(f"Upload folder: {Config.UPLOAD_FOLDER}")
    logger.info(f"Working folder: {Config.WORKING_FOLDER}")
    logger.info(f"Output folder: {Config.OUTPUT_FOLDER}")
    
    # Запуск сервера
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        threaded=True
    )
