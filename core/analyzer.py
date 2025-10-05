"""
Анализатор APK файлов
"""
import zipfile
import xml.etree.ElementTree as ET
import logging
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class APKAnalyzer:
    """Анализ структуры и содержимого APK файла"""
    
    # Android XML namespace
    ANDROID_NS = '{http://schemas.android.com/apk/res/android}'
    
    def __init__(self, apk_path: Path, request_id: str):
        """
        Инициализация анализатора
        
        Args:
            apk_path: Путь к APK файлу
            request_id: ID запроса
        """
        self.apk_path = Path(apk_path)
        self.request_id = request_id
        
        if not self.apk_path.exists():
            raise FileNotFoundError(f"APK file not found: {apk_path}")
        
        if not zipfile.is_zipfile(self.apk_path):
            raise ValueError(f"File is not a valid APK/ZIP: {apk_path}")
    
    def analyze(self) -> Dict[str, Any]:
        """
        Анализ APK файла
        
        Returns:
            Dict: Информация о APK
        """
        logger.info(f"[{self.request_id}] Analyzing APK: {self.apk_path}")
        
        info = {
            'file_name': self.apk_path.name,
            'file_size_mb': round(self.apk_path.stat().st_size / (1024 * 1024), 2),
            'package_name': None,
            'version_code': None,
            'version_name': None,
            'min_sdk': None,
            'target_sdk': None,
            'permissions': [],
            'activities': [],
            'services': [],
            'receivers': [],
            'providers': [],
            'has_native_libs': False,
            'dex_files': [],
            'files': []
        }
        
        try:
            with zipfile.ZipFile(self.apk_path, 'r') as zf:
                # Получение списка файлов
                info['files'] = zf.namelist()
                
                # Поиск DEX файлов
                info['dex_files'] = [f for f in info['files'] if f.endswith('.dex')]
                
                # Проверка наличия нативных библиотек
                info['has_native_libs'] = any(f.startswith('lib/') and f.endswith('.so') 
                                             for f in info['files'])
                
                # Попытка прочитать AndroidManifest.xml
                # Примечание: в APK манифест в бинарном формате, 
                # поэтому полный анализ возможен только после декомпиляции
                # Здесь мы делаем базовую проверку структуры
                
                if 'AndroidManifest.xml' in info['files']:
                    logger.debug(f"[{self.request_id}] AndroidManifest.xml found")
                else:
                    logger.warning(f"[{self.request_id}] AndroidManifest.xml not found")
                
                # Проверка наличия resources.arsc
                if 'resources.arsc' in info['files']:
                    logger.debug(f"[{self.request_id}] resources.arsc found")
                
                # Проверка наличия META-INF (подпись)
                meta_inf_files = [f for f in info['files'] if f.startswith('META-INF/')]
                if meta_inf_files:
                    logger.debug(f"[{self.request_id}] Found {len(meta_inf_files)} META-INF files")
        
        except Exception as e:
            logger.error(f"[{self.request_id}] Error analyzing APK: {e}")
            raise
        
        logger.info(f"[{self.request_id}] Analysis completed")
        logger.info(f"[{self.request_id}] File size: {info['file_size_mb']} MB")
        logger.info(f"[{self.request_id}] DEX files: {len(info['dex_files'])}")
        logger.info(f"[{self.request_id}] Has native libs: {info['has_native_libs']}")
        
        return info
    
    def analyze_manifest(self, manifest_path: Path) -> Dict[str, Any]:
        """
        Анализ декомпилированного AndroidManifest.xml
        
        Args:
            manifest_path: Путь к AndroidManifest.xml
            
        Returns:
            Dict: Информация из манифеста
        """
        logger.info(f"[{self.request_id}] Analyzing manifest: {manifest_path}")
        
        info = {
            'package_name': None,
            'version_code': None,
            'version_name': None,
            'min_sdk': None,
            'target_sdk': None,
            'permissions': [],
            'activities': [],
            'services': [],
            'receivers': [],
            'providers': []
        }
        
        try:
            tree = ET.parse(manifest_path)
            root = tree.getroot()
            
            # Получение package name
            info['package_name'] = root.get('package')
            
            # Получение версии
            info['version_code'] = root.get(f'{self.ANDROID_NS}versionCode')
            info['version_name'] = root.get(f'{self.ANDROID_NS}versionName')
            
            # Получение SDK версий
            uses_sdk = root.find('uses-sdk')
            if uses_sdk is not None:
                info['min_sdk'] = uses_sdk.get(f'{self.ANDROID_NS}minSdkVersion')
                info['target_sdk'] = uses_sdk.get(f'{self.ANDROID_NS}targetSdkVersion')
            
            # Получение разрешений
            for perm in root.findall('uses-permission'):
                perm_name = perm.get(f'{self.ANDROID_NS}name')
                if perm_name:
                    info['permissions'].append(perm_name)
            
            # Получение компонентов приложения
            application = root.find('application')
            if application is not None:
                # Activities
                for activity in application.findall('activity'):
                    name = activity.get(f'{self.ANDROID_NS}name')
                    if name:
                        info['activities'].append(name)
                
                # Services
                for service in application.findall('service'):
                    name = service.get(f'{self.ANDROID_NS}name')
                    if name:
                        info['services'].append(name)
                
                # Receivers
                for receiver in application.findall('receiver'):
                    name = receiver.get(f'{self.ANDROID_NS}name')
                    if name:
                        info['receivers'].append(name)
                
                # Providers
                for provider in application.findall('provider'):
                    name = provider.get(f'{self.ANDROID_NS}name')
                    if name:
                        info['providers'].append(name)
            
            logger.info(f"[{self.request_id}] Manifest analysis completed")
            logger.info(f"[{self.request_id}] Package: {info['package_name']}")
            logger.info(f"[{self.request_id}] Permissions: {len(info['permissions'])}")
            logger.info(f"[{self.request_id}] Activities: {len(info['activities'])}")
            
        except Exception as e:
            logger.error(f"[{self.request_id}] Error analyzing manifest: {e}")
            raise
        
        return info
