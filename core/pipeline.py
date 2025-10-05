"""
Главный pipeline для обработки APK файлов
"""
import logging
from pathlib import Path
from typing import Dict, Any

from config import Config
from core.analyzer import APKAnalyzer
from core.decompiler import APKDecompiler
from core.manifest_modifier import ManifestModifier
from core.obfuscator import CodeObfuscator
from core.rebuilder import APKRebuilder
from core.signer import APKSigner

logger = logging.getLogger(__name__)

class APKProcessingPipeline:
    """Pipeline для последовательной обработки APK"""
    
    def __init__(self, input_apk: Path, working_dir: Path, output_dir: Path, 
                 request_id: str, options: Dict[str, Any] = None):
        """
        Инициализация pipeline
        
        Args:
            input_apk: Путь к входному APK
            working_dir: Рабочая директория
            output_dir: Директория для выходного файла
            request_id: ID запроса
            options: Опции обработки
        """
        self.input_apk = Path(input_apk)
        self.working_dir = Path(working_dir)
        self.output_dir = Path(output_dir)
        self.request_id = request_id
        self.options = options or {}
        
        # Директории для разных этапов
        self.decompiled_dir = self.working_dir / "decompiled"
        self.modified_dir = self.working_dir / "modified"
        
        logger.info(f"[{request_id}] Pipeline initialized")
        logger.info(f"[{request_id}] Input APK: {input_apk}")
        logger.info(f"[{request_id}] Working dir: {working_dir}")
        logger.info(f"[{request_id}] Output dir: {output_dir}")
    
    def process(self) -> Path:
        """
        Выполнение полного цикла обработки
        
        Returns:
            Path: Путь к обработанному APK
        """
        try:
            # Этап 1: Анализ входного APK
            logger.info(f"[{self.request_id}] === ЭТАП 1: Анализ APK ===")
            apk_info = self._analyze()
            
            # Этап 2: Декомпиляция
            logger.info(f"[{self.request_id}] === ЭТАП 2: Декомпиляция ===")
            self._decompile()
            
            # Этап 3: Модификация манифеста
            logger.info(f"[{self.request_id}] === ЭТАП 3: Модификация манифеста ===")
            self._modify_manifest(apk_info)
            
            # Этап 4: Обфускация кода
            logger.info(f"[{self.request_id}] === ЭТАП 4: Обфускация кода ===")
            self._obfuscate_code()
            
            # Этап 5: Пересборка APK
            logger.info(f"[{self.request_id}] === ЭТАП 5: Пересборка APK ===")
            rebuilt_apk = self._rebuild()
            
            # Этап 6: Подпись APK
            logger.info(f"[{self.request_id}] === ЭТАП 6: Подпись APK ===")
            signed_apk = self._sign(rebuilt_apk)
            
            logger.info(f"[{self.request_id}] === Pipeline завершен успешно ===")
            logger.info(f"[{self.request_id}] Выходной файл: {signed_apk}")
            
            return signed_apk
            
        except Exception as e:
            logger.error(f"[{self.request_id}] Pipeline error: {e}")
            raise
    
    def _analyze(self) -> Dict[str, Any]:
        """
        Анализ APK файла
        
        Returns:
            Dict: Информация о APK
        """
        analyzer = APKAnalyzer(self.input_apk, self.request_id)
        apk_info = analyzer.analyze()
        
        logger.info(f"[{self.request_id}] Package: {apk_info.get('package_name')}")
        logger.info(f"[{self.request_id}] Version: {apk_info.get('version_name')} ({apk_info.get('version_code')})")
        logger.info(f"[{self.request_id}] Target SDK: {apk_info.get('target_sdk')}")
        logger.info(f"[{self.request_id}] Permissions: {len(apk_info.get('permissions', []))}")
        
        return apk_info
    
    def _decompile(self):
        """Декомпиляция APK"""
        decompiler = APKDecompiler(self.input_apk, self.decompiled_dir, self.request_id)
        decompiler.decompile()
        
        logger.info(f"[{self.request_id}] Decompiled to: {self.decompiled_dir}")
    
    def _modify_manifest(self, apk_info: Dict[str, Any]):
        """
        Модификация AndroidManifest.xml
        
        Args:
            apk_info: Информация о APK
        """
        manifest_path = self.decompiled_dir / "AndroidManifest.xml"
        
        if not manifest_path.exists():
            logger.warning(f"[{self.request_id}] AndroidManifest.xml not found")
            return
        
        modifier = ManifestModifier(manifest_path, self.request_id)
        
        # Получение опций из запроса или использование значений по умолчанию
        remove_permissions = self.options.get('remove_sensitive_permissions', True)
        update_sdk = self.options.get('update_target_sdk', True)
        obfuscate = self.options.get('obfuscate_manifest', True)
        
        # Удаление чувствительных разрешений
        if remove_permissions:
            removed = modifier.remove_sensitive_permissions()
            if removed:
                logger.info(f"[{self.request_id}] Removed permissions: {', '.join(removed)}")
        
        # Обновление targetSdkVersion
        if update_sdk:
            old_sdk = apk_info.get('target_sdk', 'unknown')
            modifier.update_target_sdk(Config.DEFAULT_TARGET_SDK)
            logger.info(f"[{self.request_id}] Updated targetSdkVersion: {old_sdk} -> {Config.DEFAULT_TARGET_SDK}")
        
        # Обфускация манифеста
        if obfuscate:
            modifier.obfuscate_manifest()
            logger.info(f"[{self.request_id}] Manifest obfuscated")
        
        # Сохранение изменений
        modifier.save()
        logger.info(f"[{self.request_id}] Manifest modifications saved")
    
    def _obfuscate_code(self):
        """Обфускация кода"""
        obfuscate_enabled = self.options.get('obfuscate_code', True)
        
        if not obfuscate_enabled:
            logger.info(f"[{self.request_id}] Code obfuscation disabled")
            return
        
        obfuscator = CodeObfuscator(self.decompiled_dir, self.request_id)
        
        # Выполнение различных техник обфускации
        if Config.OBFUSCATION_TECHNIQUES.get('rename_classes'):
            obfuscator.rename_classes()
        
        if Config.OBFUSCATION_TECHNIQUES.get('rename_methods'):
            obfuscator.rename_methods()
        
        if Config.OBFUSCATION_TECHNIQUES.get('rename_fields'):
            obfuscator.rename_fields()
        
        if Config.OBFUSCATION_TECHNIQUES.get('encrypt_strings'):
            obfuscator.encrypt_strings()
        
        if Config.OBFUSCATION_TECHNIQUES.get('remove_debug_info'):
            obfuscator.remove_debug_info()
        
        logger.info(f"[{self.request_id}] Code obfuscation completed")
    
    def _rebuild(self) -> Path:
        """
        Пересборка APK
        
        Returns:
            Path: Путь к пересобранному APK
        """
        output_apk = self.working_dir / "rebuilt.apk"
        
        rebuilder = APKRebuilder(self.decompiled_dir, output_apk, self.request_id)
        rebuilder.rebuild()
        
        logger.info(f"[{self.request_id}] APK rebuilt: {output_apk}")
        
        return output_apk
    
    def _sign(self, apk_path: Path) -> Path:
        """
        Подпись APK
        
        Args:
            apk_path: Путь к неподписанному APK
            
        Returns:
            Path: Путь к подписанному APK
        """
        output_apk = self.output_dir / "protected.apk"
        
        signer = APKSigner(self.request_id)
        signer.sign(apk_path, output_apk)
        
        logger.info(f"[{self.request_id}] APK signed: {output_apk}")
        
        return output_apk
