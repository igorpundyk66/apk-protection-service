"""
API endpoints для обработки APK файлов
"""
from flask import Blueprint, request, send_file, jsonify
from werkzeug.utils import secure_filename
from pathlib import Path
import uuid
import logging
import traceback

from config import Config
from core.pipeline import APKProcessingPipeline
from utils.file_manager import FileManager

# Создание Blueprint
api_bp = Blueprint('api', __name__)
logger = logging.getLogger(__name__)

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Проверка здоровья сервиса"""
    return jsonify({
        "status": "healthy",
        "service": "APK Protection Service",
        "version": "1.0.0"
    }), 200

@api_bp.route('/process', methods=['POST'])
def process_apk():
    """
    Основной endpoint для обработки APK файлов
    
    Принимает:
        - file: APK файл (multipart/form-data)
        - options: JSON с опциями обработки (опционально)
    
    Возвращает:
        - Защищенный APK файл
    """
    request_id = str(uuid.uuid4())
    logger.info(f"[{request_id}] Получен запрос на обработку APK")
    
    file_manager = None
    
    try:
        # Валидация запроса
        if 'file' not in request.files:
            logger.warning(f"[{request_id}] Файл не предоставлен")
            return jsonify({"error": "Файл не предоставлен"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            logger.warning(f"[{request_id}] Пустое имя файла")
            return jsonify({"error": "Файл не выбран"}), 400
        
        if not Config.is_allowed_file(file.filename):
            logger.warning(f"[{request_id}] Недопустимый тип файла: {file.filename}")
            return jsonify({"error": "Недопустимый тип файла. Разрешены только .apk файлы"}), 400
        
        # Получение опций обработки
        options = {}
        if 'options' in request.form:
            import json
            try:
                options = json.loads(request.form['options'])
            except json.JSONDecodeError:
                logger.warning(f"[{request_id}] Некорректный JSON в options")
        
        logger.info(f"[{request_id}] Обработка файла: {file.filename}")
        logger.info(f"[{request_id}] Опции: {options}")
        
        # Создание файлового менеджера
        file_manager = FileManager(request_id)
        
        # Сохранение загруженного файла
        original_filename = secure_filename(file.filename)
        input_path = file_manager.save_upload(file, original_filename)
        logger.info(f"[{request_id}] Файл сохранен: {input_path}")
        
        # Создание pipeline для обработки
        pipeline = APKProcessingPipeline(
            input_apk=input_path,
            working_dir=file_manager.working_dir,
            output_dir=file_manager.output_dir,
            request_id=request_id,
            options=options
        )
        
        # Запуск обработки
        logger.info(f"[{request_id}] Запуск pipeline обработки")
        output_apk = pipeline.process()
        logger.info(f"[{request_id}] Обработка завершена: {output_apk}")
        
        # Проверка результата
        if not output_apk.exists():
            raise FileNotFoundError(f"Выходной файл не найден: {output_apk}")
        
        # Формирование имени выходного файла
        output_filename = f"protected_{original_filename}"
        
        # Отправка файла клиенту
        logger.info(f"[{request_id}] Отправка файла клиенту: {output_filename}")
        
        response = send_file(
            output_apk,
            as_attachment=True,
            download_name=output_filename,
            mimetype='application/vnd.android.package-archive'
        )
        
        # Очистка будет выполнена после отправки файла
        # Flask автоматически вызовет after_request
        
        return response
        
    except FileNotFoundError as e:
        logger.error(f"[{request_id}] Файл не найден: {e}")
        return jsonify({
            "error": "Файл не найден",
            "details": str(e)
        }), 404
        
    except ValueError as e:
        logger.error(f"[{request_id}] Ошибка валидации: {e}")
        return jsonify({
            "error": "Ошибка валидации",
            "details": str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"[{request_id}] Ошибка обработки: {e}")
        logger.error(f"[{request_id}] Traceback: {traceback.format_exc()}")
        return jsonify({
            "error": "Ошибка обработки APK",
            "details": str(e),
            "request_id": request_id
        }), 500
        
    finally:
        # Очистка временных файлов
        if file_manager:
            try:
                # Задержка очистки, чтобы файл успел отправиться
                # В production лучше использовать фоновую задачу
                import threading
                import time
                
                def delayed_cleanup():
                    time.sleep(5)  # Ждем 5 секунд
                    try:
                        file_manager.cleanup()
                        logger.info(f"[{request_id}] Временные файлы очищены")
                    except Exception as e:
                        logger.error(f"[{request_id}] Ошибка очистки: {e}")
                
                cleanup_thread = threading.Thread(target=delayed_cleanup)
                cleanup_thread.daemon = True
                cleanup_thread.start()
                
            except Exception as e:
                logger.error(f"[{request_id}] Ошибка запуска очистки: {e}")

@api_bp.route('/info', methods=['GET'])
def get_info():
    """Получение информации о сервисе"""
    return jsonify({
        "service": "APK Protection Service",
        "version": "1.0.0",
        "description": "Сервис для защиты и обфускации Android APK файлов",
        "features": [
            "Удаление чувствительных разрешений",
            "Обновление targetSdkVersion",
            "Обфускация кода (классы, методы, поля)",
            "Шифрование строковых констант",
            "Обфускация манифеста",
            "Новая подпись APK"
        ],
        "max_file_size_mb": Config.MAX_CONTENT_LENGTH // (1024 * 1024),
        "supported_formats": [".apk"]
    }), 200
