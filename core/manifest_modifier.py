"""
Модификатор AndroidManifest.xml
"""
import xml.etree.ElementTree as ET
import logging
import random
from pathlib import Path
from typing import List

from config import Config

logger = logging.getLogger(__name__)

class ManifestModifier:
    """Модификация AndroidManifest.xml"""
    
    # Android XML namespace
    ANDROID_NS = 'http://schemas.android.com/apk/res/android'
    
    def __init__(self, manifest_path: Path, request_id: str):
        """
        Инициализация модификатора
        
        Args:
            manifest_path: Путь к AndroidManifest.xml
            request_id: ID запроса
        """
        self.manifest_path = Path(manifest_path)
        self.request_id = request_id
        
        if not self.manifest_path.exists():
            raise FileNotFoundError(f"Manifest not found: {manifest_path}")
        
        # Регистрация namespace
        ET.register_namespace('android', self.ANDROID_NS)
        
        # Загрузка манифеста
        self.tree = ET.parse(self.manifest_path)
        self.root = self.tree.getroot()
        
        logger.debug(f"[{request_id}] Manifest loaded: {manifest_path}")
    
    def remove_sensitive_permissions(self) -> List[str]:
        """
        Удаление чувствительных разрешений
        
        Returns:
            List[str]: Список удаленных разрешений
        """
        logger.info(f"[{self.request_id}] Removing sensitive permissions")
        
        removed_permissions = []
        
        # Поиск всех uses-permission элементов
        for perm_elem in self.root.findall('uses-permission'):
            perm_name = perm_elem.get(f'{{{self.ANDROID_NS}}}name')
            
            if perm_name in Config.SENSITIVE_PERMISSIONS:
                logger.info(f"[{self.request_id}] Removing permission: {perm_name}")
                self.root.remove(perm_elem)
                removed_permissions.append(perm_name)
        
        logger.info(f"[{self.request_id}] Removed {len(removed_permissions)} permissions")
        
        return removed_permissions
    
    def update_target_sdk(self, target_sdk: int):
        """
        Обновление targetSdkVersion
        
        Args:
            target_sdk: Целевая версия SDK
        """
        logger.info(f"[{self.request_id}] Updating targetSdkVersion to {target_sdk}")
        
        # Поиск uses-sdk элемента
        uses_sdk = self.root.find('uses-sdk')
        
        if uses_sdk is None:
            # Создание нового элемента если не существует
            uses_sdk = ET.SubElement(self.root, 'uses-sdk')
            logger.debug(f"[{self.request_id}] Created new uses-sdk element")
        
        # Обновление targetSdkVersion
        uses_sdk.set(f'{{{self.ANDROID_NS}}}targetSdkVersion', str(target_sdk))
        
        # Также обновляем compileSdkVersion если есть
        compile_sdk_attr = f'{{{self.ANDROID_NS}}}compileSdkVersion'
        if compile_sdk_attr in uses_sdk.attrib:
            uses_sdk.set(compile_sdk_attr, str(target_sdk))
        
        logger.info(f"[{self.request_id}] targetSdkVersion updated to {target_sdk}")
    
    def obfuscate_manifest(self):
        """Обфускация манифеста"""
        logger.info(f"[{self.request_id}] Obfuscating manifest")
        
        # 1. Перемешивание порядка разрешений
        self._shuffle_permissions()
        
        # 2. Добавление фиктивных метаданных
        self._add_fake_metadata()
        
        logger.info(f"[{self.request_id}] Manifest obfuscation completed")
    
    def _shuffle_permissions(self):
        """Перемешивание порядка разрешений"""
        # Получение всех uses-permission элементов
        permissions = self.root.findall('uses-permission')
        
        if len(permissions) < 2:
            return
        
        # Удаление всех разрешений
        for perm in permissions:
            self.root.remove(perm)
        
        # Перемешивание
        random.shuffle(permissions)
        
        # Вставка обратно в случайном порядке
        # Находим позицию для вставки (после package declaration, но до application)
        insert_index = 0
        for i, elem in enumerate(self.root):
            if elem.tag == 'application':
                insert_index = i
                break
        
        # Вставка разрешений
        for i, perm in enumerate(permissions):
            self.root.insert(insert_index + i, perm)
        
        logger.debug(f"[{self.request_id}] Shuffled {len(permissions)} permissions")
    
    def _add_fake_metadata(self):
        """Добавление фиктивных метаданных в application"""
        application = self.root.find('application')
        
        if application is None:
            logger.warning(f"[{self.request_id}] Application element not found")
            return
        
        # Список фиктивных метаданных
        fake_metadata = [
            ('com.google.android.gms.version', '@integer/google_play_services_version'),
            ('com.google.android.gms.ads.APPLICATION_ID', 'ca-app-pub-0000000000000000~0000000000'),
            ('firebase_analytics_collection_enabled', 'true'),
            ('google_analytics_automatic_screen_reporting_enabled', 'false'),
        ]
        
        # Добавление случайных метаданных
        num_to_add = random.randint(1, len(fake_metadata))
        selected_metadata = random.sample(fake_metadata, num_to_add)
        
        for name, value in selected_metadata:
            # Проверка что метаданные еще не существуют
            existing = application.find(f".//meta-data[@{{}}name='{name}']")
            if existing is None:
                meta_elem = ET.SubElement(application, 'meta-data')
                meta_elem.set(f'{{{self.ANDROID_NS}}}name', name)
                meta_elem.set(f'{{{self.ANDROID_NS}}}value', value)
                logger.debug(f"[{self.request_id}] Added fake metadata: {name}")
    
    def change_package_name(self, new_package_name: str):
        """
        Изменение имени пакета
        
        Args:
            new_package_name: Новое имя пакета
        """
        logger.info(f"[{self.request_id}] Changing package name to: {new_package_name}")
        
        old_package = self.root.get('package')
        self.root.set('package', new_package_name)
        
        logger.info(f"[{self.request_id}] Package name changed: {old_package} -> {new_package_name}")
    
    def save(self):
        """Сохранение изменений в файл"""
        logger.info(f"[{self.request_id}] Saving manifest: {self.manifest_path}")
        
        try:
            # Сохранение с правильным форматированием
            self.tree.write(
                self.manifest_path,
                encoding='utf-8',
                xml_declaration=True
            )
            
            logger.info(f"[{self.request_id}] Manifest saved successfully")
            
        except Exception as e:
            logger.error(f"[{self.request_id}] Error saving manifest: {e}")
            raise
