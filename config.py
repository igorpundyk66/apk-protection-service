"""
Конфигурация сервиса защиты APK
"""
import os
from pathlib import Path

# Базовая директория проекта
BASE_DIR = Path(__file__).parent.absolute()

class Config:
    """Основная конфигурация приложения"""
    
    # Flask настройки
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)
    MAX_CONTENT_LENGTH = 150 * 1024 * 1024  # 150 MB максимальный размер файла
    
    # Директории
    UPLOAD_FOLDER = BASE_DIR / "temp" / "uploads"
    WORKING_FOLDER = BASE_DIR / "temp" / "working"
    OUTPUT_FOLDER = BASE_DIR / "temp" / "output"
    FRONTEND_FOLDER = BASE_DIR / "frontend"
    
    # Создание директорий если не существуют
    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
    WORKING_FOLDER.mkdir(parents=True, exist_ok=True)
    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
    
    # Пути к Android инструментам
    APKTOOL_PATH = "apktool"
    APKSIGNER_PATH = "apksigner"
    ZIPALIGN_PATH = "zipalign"
    KEYTOOL_PATH = "keytool"
    
    # Obfuscapk (если используется)
    OBFUSCAPK_PATH = "/tmp/Obfuscapk"
    USE_OBFUSCAPK = False  # Будем использовать собственную реализацию
    
    # APK настройки
    DEFAULT_TARGET_SDK = 33  # Android 13
    DEFAULT_MIN_SDK = 21     # Android 5.0
    
    # Чувствительные разрешения для удаления
    SENSITIVE_PERMISSIONS = [
        "android.permission.RECEIVE_SMS",
        "android.permission.READ_SMS",
        "android.permission.SEND_SMS",
        "android.permission.WRITE_SMS",
        "android.permission.BIND_NOTIFICATION_LISTENER_SERVICE",
        "android.permission.BIND_ACCESSIBILITY_SERVICE",
        "android.permission.SYSTEM_ALERT_WINDOW",
        "android.permission.REQUEST_INSTALL_PACKAGES",
    ]
    
    # Keystore настройки
    KEYSTORE_FOLDER = BASE_DIR / "temp"
    KEYSTORE_FILE = KEYSTORE_FOLDER / "release.keystore"
    KEYSTORE_PASSWORD = "apkprotect2025"
    KEY_ALIAS = "apkprotectkey"
    KEY_PASSWORD = "apkprotect2025"
    KEY_VALIDITY_DAYS = 10000
    KEY_DN = "CN=APK Protection Service, OU=Security, O=APKProtect, L=City, ST=State, C=US"
    
    # Обфускация настройки
    OBFUSCATION_TECHNIQUES = {
        "rename_classes": True,
        "rename_methods": True,
        "rename_fields": True,
        "encrypt_strings": True,
        "obfuscate_manifest": True,
        "remove_debug_info": True,
    }
    
    # Логирование
    LOG_LEVEL = "INFO"
    LOG_FILE = BASE_DIR / "temp" / "app.log"
    
    # Таймауты (секунды)
    APKTOOL_TIMEOUT = 300  # 5 минут
    SIGNING_TIMEOUT = 60   # 1 минута
    
    # Разрешенные расширения файлов
    ALLOWED_EXTENSIONS = {'.apk'}
    
    @staticmethod
    def is_allowed_file(filename):
        """Проверка разрешенного расширения файла"""
        return Path(filename).suffix.lower() in Config.ALLOWED_EXTENSIONS
