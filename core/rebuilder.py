"""
Пересборка APK файлов
"""
import logging
from pathlib import Path

from config import Config
from utils.helpers import run_command

logger = logging.getLogger(__name__)

class APKRebuilder:
    """Пересборка APK с использованием apktool"""
    
    def __init__(self, decompiled_dir: Path, output_apk: Path, request_id: str):
        """
        Инициализация rebuilder
        
        Args:
            decompiled_dir: Директория с декомпилированными файлами
            output_apk: Путь для выходного APK
            request_id: ID запроса
        """
        self.decompiled_dir = Path(decompiled_dir)
        self.output_apk = Path(output_apk)
        self.request_id = request_id
        
        if not self.decompiled_dir.exists():
            raise FileNotFoundError(f"Decompiled directory not found: {decompiled_dir}")
    
    def rebuild(self):
        """Пересборка APK файла"""
        logger.info(f"[{self.request_id}] Rebuilding APK")
        logger.info(f"[{self.request_id}] Input directory: {self.decompiled_dir}")
        logger.info(f"[{self.request_id}] Output APK: {self.output_apk}")
        
        # Удаление выходного файла если существует
        if self.output_apk.exists():
            self.output_apk.unlink()
            logger.debug(f"[{self.request_id}] Removed existing output file")
        
        # Команда apktool build
        cmd = [
            Config.APKTOOL_PATH,
            'b',  # build
            str(self.decompiled_dir),
            '-o', str(self.output_apk),
            '-f',  # force overwrite
        ]
        
        try:
            stdout, stderr, returncode = run_command(
                cmd,
                timeout=Config.APKTOOL_TIMEOUT
            )
            
            logger.info(f"[{self.request_id}] Rebuild completed successfully")
            
            # Проверка результата
            if not self.output_apk.exists():
                raise RuntimeError("Output APK was not created")
            
            # Проверка размера файла
            file_size_mb = self.output_apk.stat().st_size / (1024 * 1024)
            logger.info(f"[{self.request_id}] Output APK size: {file_size_mb:.2f} MB")
            
            if file_size_mb < 0.1:
                logger.warning(f"[{self.request_id}] Output APK is suspiciously small")
            
        except Exception as e:
            logger.error(f"[{self.request_id}] Rebuild failed: {e}")
            raise RuntimeError(f"Failed to rebuild APK: {e}")
