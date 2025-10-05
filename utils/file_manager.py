"""
Менеджер для управления временными файлами
"""
import shutil
from pathlib import Path
import logging

from config import Config

logger = logging.getLogger(__name__)

class FileManager:
    """Управление временными файлами и директориями"""
    
    def __init__(self, request_id):
        """
        Инициализация файлового менеджера
        
        Args:
            request_id: Уникальный идентификатор запроса
        """
        self.request_id = request_id
        
        # Создание уникальных директорий для этого запроса
        self.upload_dir = Config.UPLOAD_FOLDER / request_id
        self.working_dir = Config.WORKING_FOLDER / request_id
        self.output_dir = Config.OUTPUT_FOLDER / request_id
        
        # Создание директорий
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.working_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.debug(f"[{request_id}] FileManager initialized")
        logger.debug(f"[{request_id}] Upload dir: {self.upload_dir}")
        logger.debug(f"[{request_id}] Working dir: {self.working_dir}")
        logger.debug(f"[{request_id}] Output dir: {self.output_dir}")
    
    def save_upload(self, file, filename):
        """
        Сохранение загруженного файла
        
        Args:
            file: Файловый объект из request.files
            filename: Имя файла
            
        Returns:
            Path: Путь к сохраненному файлу
        """
        file_path = self.upload_dir / filename
        file.save(str(file_path))
        logger.info(f"[{self.request_id}] File saved: {file_path}")
        return file_path
    
    def get_working_path(self, subdir=None):
        """
        Получение пути в рабочей директории
        
        Args:
            subdir: Поддиректория (опционально)
            
        Returns:
            Path: Путь в рабочей директории
        """
        if subdir:
            path = self.working_dir / subdir
            path.mkdir(parents=True, exist_ok=True)
            return path
        return self.working_dir
    
    def get_output_path(self, filename):
        """
        Получение пути для выходного файла
        
        Args:
            filename: Имя файла
            
        Returns:
            Path: Путь к выходному файлу
        """
        return self.output_dir / filename
    
    def cleanup(self):
        """Очистка всех временных файлов и директорий"""
        try:
            # Удаление upload директории
            if self.upload_dir.exists():
                shutil.rmtree(self.upload_dir)
                logger.debug(f"[{self.request_id}] Removed upload dir: {self.upload_dir}")
            
            # Удаление working директории
            if self.working_dir.exists():
                shutil.rmtree(self.working_dir)
                logger.debug(f"[{self.request_id}] Removed working dir: {self.working_dir}")
            
            # Удаление output директории
            if self.output_dir.exists():
                shutil.rmtree(self.output_dir)
                logger.debug(f"[{self.request_id}] Removed output dir: {self.output_dir}")
            
            logger.info(f"[{self.request_id}] Cleanup completed")
            
        except Exception as e:
            logger.error(f"[{self.request_id}] Cleanup error: {e}")
            raise
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup"""
        self.cleanup()
        return False
