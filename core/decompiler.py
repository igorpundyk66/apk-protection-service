"""
Декомпилятор APK файлов
"""
import logging
from pathlib import Path

from config import Config
from utils.helpers import run_command

logger = logging.getLogger(__name__)

class APKDecompiler:
    """Декомпиляция APK с использованием apktool"""
    
    def __init__(self, apk_path: Path, output_dir: Path, request_id: str):
        """
        Инициализация декомпилятора
        
        Args:
            apk_path: Путь к APK файлу
            output_dir: Директория для декомпилированных файлов
            request_id: ID запроса
        """
        self.apk_path = Path(apk_path)
        self.output_dir = Path(output_dir)
        self.request_id = request_id
        
        if not self.apk_path.exists():
            raise FileNotFoundError(f"APK file not found: {apk_path}")
    
    def decompile(self):
        """Декомпиляция APK файла"""
        logger.info(f"[{self.request_id}] Decompiling APK: {self.apk_path}")
        logger.info(f"[{self.request_id}] Output directory: {self.output_dir}")
        
        # Создание выходной директории
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Команда apktool decode
        cmd = [
            Config.APKTOOL_PATH,
            'd',  # decode
            str(self.apk_path),
            '-o', str(self.output_dir),
            '-f',  # force overwrite
            '--no-debug-info',  # не включать отладочную информацию
        ]
        
        try:
            stdout, stderr, returncode = run_command(
                cmd, 
                timeout=Config.APKTOOL_TIMEOUT
            )
            
            logger.info(f"[{self.request_id}] Decompilation completed successfully")
            
            # Проверка результата
            if not self.output_dir.exists():
                raise RuntimeError("Output directory was not created")
            
            manifest_path = self.output_dir / "AndroidManifest.xml"
            if not manifest_path.exists():
                raise RuntimeError("AndroidManifest.xml not found in decompiled output")
            
            logger.info(f"[{self.request_id}] Decompiled files verified")
            
        except Exception as e:
            logger.error(f"[{self.request_id}] Decompilation failed: {e}")
            raise RuntimeError(f"Failed to decompile APK: {e}")
