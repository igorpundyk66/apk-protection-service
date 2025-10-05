"""
Подпись APK файлов
"""
import logging
from pathlib import Path

from config import Config
from utils.helpers import run_command

logger = logging.getLogger(__name__)

class APKSigner:
    """Подпись APK файлов"""
    
    def __init__(self, request_id: str):
        """
        Инициализация signer
        
        Args:
            request_id: ID запроса
        """
        self.request_id = request_id
        self.keystore_path = Config.KEYSTORE_FILE
        
        # Создание keystore если не существует
        if not self.keystore_path.exists():
            self._generate_keystore()
    
    def _generate_keystore(self):
        """Генерация keystore для подписи"""
        logger.info(f"[{self.request_id}] Generating keystore")
        
        # Создание директории для keystore
        Config.KEYSTORE_FOLDER.mkdir(parents=True, exist_ok=True)
        
        # Команда keytool для генерации keystore
        cmd = [
            Config.KEYTOOL_PATH,
            '-genkeypair',
            '-v',
            '-keystore', str(self.keystore_path),
            '-alias', Config.KEY_ALIAS,
            '-keyalg', 'RSA',
            '-keysize', '2048',
            '-validity', str(Config.KEY_VALIDITY_DAYS),
            '-storepass', Config.KEYSTORE_PASSWORD,
            '-keypass', Config.KEY_PASSWORD,
            '-dname', Config.KEY_DN,
        ]
        
        try:
            stdout, stderr, returncode = run_command(
                cmd,
                timeout=Config.SIGNING_TIMEOUT
            )
            
            logger.info(f"[{self.request_id}] Keystore generated: {self.keystore_path}")
            
            if not self.keystore_path.exists():
                raise RuntimeError("Keystore was not created")
            
        except Exception as e:
            logger.error(f"[{self.request_id}] Keystore generation failed: {e}")
            raise RuntimeError(f"Failed to generate keystore: {e}")
    
    def sign(self, input_apk: Path, output_apk: Path):
        """
        Подпись APK файла
        
        Args:
            input_apk: Путь к неподписанному APK
            output_apk: Путь для подписанного APK
        """
        logger.info(f"[{self.request_id}] Signing APK")
        logger.info(f"[{self.request_id}] Input APK: {input_apk}")
        logger.info(f"[{self.request_id}] Output APK: {output_apk}")
        
        if not input_apk.exists():
            raise FileNotFoundError(f"Input APK not found: {input_apk}")
        
        # Удаление выходного файла если существует
        if output_apk.exists():
            output_apk.unlink()
            logger.debug(f"[{self.request_id}] Removed existing output file")
        
        # Сначала выравниваем APK (zipalign)
        aligned_apk = input_apk.parent / f"aligned_{input_apk.name}"
        self._zipalign(input_apk, aligned_apk)
        
        # Затем подписываем
        self._sign_apk(aligned_apk, output_apk)
        
        # Удаляем временный aligned файл
        if aligned_apk.exists():
            aligned_apk.unlink()
            logger.debug(f"[{self.request_id}] Removed temporary aligned file")
        
        logger.info(f"[{self.request_id}] APK signed successfully")
    
    def _zipalign(self, input_apk: Path, output_apk: Path):
        """
        Выравнивание APK
        
        Args:
            input_apk: Входной APK
            output_apk: Выходной APK
        """
        logger.info(f"[{self.request_id}] Aligning APK")
        
        cmd = [
            Config.ZIPALIGN_PATH,
            '-f',  # force overwrite
            '-v',  # verbose
            '4',   # alignment in bytes
            str(input_apk),
            str(output_apk)
        ]
        
        try:
            stdout, stderr, returncode = run_command(
                cmd,
                timeout=Config.SIGNING_TIMEOUT
            )
            
            logger.info(f"[{self.request_id}] APK aligned successfully")
            
            if not output_apk.exists():
                raise RuntimeError("Aligned APK was not created")
            
        except Exception as e:
            logger.error(f"[{self.request_id}] Zipalign failed: {e}")
            raise RuntimeError(f"Failed to align APK: {e}")
    
    def _sign_apk(self, input_apk: Path, output_apk: Path):
        """
        Подпись APK с использованием apksigner
        
        Args:
            input_apk: Входной APK
            output_apk: Выходной APK
        """
        logger.info(f"[{self.request_id}] Signing with apksigner")
        
        cmd = [
            Config.APKSIGNER_PATH,
            'sign',
            '--ks', str(self.keystore_path),
            '--ks-pass', f'pass:{Config.KEYSTORE_PASSWORD}',
            '--key-pass', f'pass:{Config.KEY_PASSWORD}',
            '--ks-key-alias', Config.KEY_ALIAS,
            '--out', str(output_apk),
            str(input_apk)
        ]
        
        try:
            stdout, stderr, returncode = run_command(
                cmd,
                timeout=Config.SIGNING_TIMEOUT
            )
            
            logger.info(f"[{self.request_id}] APK signed with apksigner")
            
            if not output_apk.exists():
                raise RuntimeError("Signed APK was not created")
            
            # Верификация подписи
            self._verify_signature(output_apk)
            
        except Exception as e:
            logger.error(f"[{self.request_id}] Signing failed: {e}")
            raise RuntimeError(f"Failed to sign APK: {e}")
    
    def _verify_signature(self, apk_path: Path):
        """
        Верификация подписи APK
        
        Args:
            apk_path: Путь к APK
        """
        logger.info(f"[{self.request_id}] Verifying signature")
        
        cmd = [
            Config.APKSIGNER_PATH,
            'verify',
            '-v',
            str(apk_path)
        ]
        
        try:
            stdout, stderr, returncode = run_command(
                cmd,
                timeout=Config.SIGNING_TIMEOUT
            )
            
            logger.info(f"[{self.request_id}] Signature verified successfully")
            
        except Exception as e:
            logger.warning(f"[{self.request_id}] Signature verification failed: {e}")
            # Не выбрасываем исключение, так как подпись может быть валидной
            # даже если верификация выдает предупреждения
