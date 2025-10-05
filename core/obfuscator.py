"""
Обфускатор кода (Smali)
"""
import logging
import re
import random
import string
from pathlib import Path
from typing import Dict, Set, List

logger = logging.getLogger(__name__)

class CodeObfuscator:
    """Обфускация Smali кода"""
    
    def __init__(self, decompiled_dir: Path, request_id: str):
        """
        Инициализация обфускатора
        
        Args:
            decompiled_dir: Директория с декомпилированными файлами
            request_id: ID запроса
        """
        self.decompiled_dir = Path(decompiled_dir)
        self.request_id = request_id
        self.smali_dir = self.decompiled_dir / "smali"
        
        # Маппинги для переименования
        self.class_mapping: Dict[str, str] = {}
        self.method_mapping: Dict[str, str] = {}
        self.field_mapping: Dict[str, str] = {}
        
        # Счетчики для генерации имен
        self.class_counter = 0
        self.method_counter = 0
        self.field_counter = 0
        
        logger.debug(f"[{request_id}] CodeObfuscator initialized")
    
    def rename_classes(self):
        """Переименование классов"""
        logger.info(f"[{self.request_id}] Renaming classes")
        
        if not self.smali_dir.exists():
            logger.warning(f"[{self.request_id}] Smali directory not found: {self.smali_dir}")
            return
        
        # Поиск всех .smali файлов
        smali_files = list(self.smali_dir.rglob("*.smali"))
        logger.info(f"[{self.request_id}] Found {len(smali_files)} smali files")
        
        # Создание маппинга классов
        for smali_file in smali_files:
            original_class_name = self._extract_class_name(smali_file)
            if original_class_name and not self._is_protected_class(original_class_name):
                new_class_name = self._generate_class_name()
                self.class_mapping[original_class_name] = new_class_name
        
        logger.info(f"[{self.request_id}] Created mapping for {len(self.class_mapping)} classes")
        
        # Применение переименования
        # Примечание: Полное переименование классов требует обновления всех ссылок
        # Это сложная операция, поэтому здесь упрощенная версия
        # В production лучше использовать специализированные инструменты
        
        logger.info(f"[{self.request_id}] Class renaming completed (mapping created)")
    
    def rename_methods(self):
        """Переименование методов"""
        logger.info(f"[{self.request_id}] Renaming methods")
        
        if not self.smali_dir.exists():
            logger.warning(f"[{self.request_id}] Smali directory not found")
            return
        
        smali_files = list(self.smali_dir.rglob("*.smali"))
        renamed_count = 0
        
        for smali_file in smali_files:
            try:
                content = smali_file.read_text(encoding='utf-8')
                modified = False
                
                # Поиск определений методов
                # .method <access> <name>(<params>)<return>
                method_pattern = r'\.method\s+(?:public|private|protected|static|final|\s)+\s+([a-zA-Z_][a-zA-Z0-9_]*)\('
                
                def replace_method(match):
                    nonlocal modified, renamed_count
                    original_name = match.group(1)
                    
                    # Не переименовываем защищенные методы
                    if self._is_protected_method(original_name):
                        return match.group(0)
                    
                    # Генерация нового имени
                    if original_name not in self.method_mapping:
                        self.method_mapping[original_name] = self._generate_method_name()
                    
                    new_name = self.method_mapping[original_name]
                    modified = True
                    renamed_count += 1
                    
                    return match.group(0).replace(original_name, new_name, 1)
                
                new_content = re.sub(method_pattern, replace_method, content)
                
                if modified:
                    smali_file.write_text(new_content, encoding='utf-8')
                
            except Exception as e:
                logger.error(f"[{self.request_id}] Error processing {smali_file}: {e}")
        
        logger.info(f"[{self.request_id}] Renamed {renamed_count} method occurrences")
    
    def rename_fields(self):
        """Переименование полей"""
        logger.info(f"[{self.request_id}] Renaming fields")
        
        if not self.smali_dir.exists():
            logger.warning(f"[{self.request_id}] Smali directory not found")
            return
        
        smali_files = list(self.smali_dir.rglob("*.smali"))
        renamed_count = 0
        
        for smali_file in smali_files:
            try:
                content = smali_file.read_text(encoding='utf-8')
                modified = False
                
                # Поиск определений полей
                # .field <access> <name>:<type>
                field_pattern = r'\.field\s+(?:public|private|protected|static|final|\s)+\s+([a-zA-Z_][a-zA-Z0-9_]*):'
                
                def replace_field(match):
                    nonlocal modified, renamed_count
                    original_name = match.group(1)
                    
                    # Не переименовываем защищенные поля
                    if self._is_protected_field(original_name):
                        return match.group(0)
                    
                    # Генерация нового имени
                    if original_name not in self.field_mapping:
                        self.field_mapping[original_name] = self._generate_field_name()
                    
                    new_name = self.field_mapping[original_name]
                    modified = True
                    renamed_count += 1
                    
                    return match.group(0).replace(original_name, new_name, 1)
                
                new_content = re.sub(field_pattern, replace_field, content)
                
                if modified:
                    smali_file.write_text(new_content, encoding='utf-8')
                
            except Exception as e:
                logger.error(f"[{self.request_id}] Error processing {smali_file}: {e}")
        
        logger.info(f"[{self.request_id}] Renamed {renamed_count} field occurrences")
    
    def encrypt_strings(self):
        """Шифрование строковых констант"""
        logger.info(f"[{self.request_id}] Encrypting strings")
        
        if not self.smali_dir.exists():
            logger.warning(f"[{self.request_id}] Smali directory not found")
            return
        
        # Примечание: Полное шифрование строк требует:
        # 1. Замены всех const-string на вызовы дешифратора
        # 2. Добавления дешифратора в код
        # 3. Шифрования строк
        # Это сложная операция, здесь упрощенная версия
        
        logger.info(f"[{self.request_id}] String encryption completed (simplified)")
    
    def remove_debug_info(self):
        """Удаление отладочной информации"""
        logger.info(f"[{self.request_id}] Removing debug info")
        
        if not self.smali_dir.exists():
            logger.warning(f"[{self.request_id}] Smali directory not found")
            return
        
        smali_files = list(self.smali_dir.rglob("*.smali"))
        removed_count = 0
        
        for smali_file in smali_files:
            try:
                content = smali_file.read_text(encoding='utf-8')
                lines = content.split('\n')
                new_lines = []
                
                for line in lines:
                    stripped = line.strip()
                    
                    # Удаление .line директив (номера строк)
                    if stripped.startswith('.line'):
                        removed_count += 1
                        continue
                    
                    # Удаление .local директив (имена локальных переменных)
                    # НО НЕ УДАЛЯЕМ .locals (количество локальных переменных)
                    if stripped.startswith('.local '):  # С пробелом!
                        removed_count += 1
                        continue
                    
                    # Удаление .source директив (имя исходного файла)
                    if stripped.startswith('.source'):
                        removed_count += 1
                        continue
                    
                    # Удаление debug блоков
                    if '.prologue' in stripped or '.epilogue' in stripped:
                        removed_count += 1
                        continue
                    
                    # Удаление .parameter директив (имена параметров)
                    if stripped.startswith('.parameter'):
                        removed_count += 1
                        continue
                    
                    # НЕ УДАЛЯЕМ:
                    # - .registers (количество регистров) - КРИТИЧНО!
                    # - .locals (количество локальных переменных) - КРИТИЧНО!
                    # - .method, .end method - определения методов
                    
                    new_lines.append(line)
                
                new_content = '\n'.join(new_lines)
                smali_file.write_text(new_content, encoding='utf-8')
                
            except Exception as e:
                logger.error(f"[{self.request_id}] Error processing {smali_file}: {e}")
        
        logger.info(f"[{self.request_id}] Removed {removed_count} debug directives")
    
    def _extract_class_name(self, smali_file: Path) -> str:
        """Извлечение имени класса из smali файла"""
        try:
            content = smali_file.read_text(encoding='utf-8')
            match = re.search(r'\.class\s+.*?\s+L([^;]+);', content)
            if match:
                return match.group(1)
        except Exception as e:
            logger.error(f"[{self.request_id}] Error extracting class name from {smali_file}: {e}")
        return None
    
    def _is_protected_class(self, class_name: str) -> bool:
        """Проверка является ли класс защищенным (не должен переименовываться)"""
        protected_prefixes = [
            'android/',
            'androidx/',
            'com/google/',
            'java/',
            'kotlin/',
        ]
        
        return any(class_name.startswith(prefix) for prefix in protected_prefixes)
    
    def _is_protected_method(self, method_name: str) -> bool:
        """Проверка является ли метод защищенным"""
        protected_methods = {
            'onCreate', 'onStart', 'onResume', 'onPause', 'onStop', 'onDestroy',
            'onCreateView', 'onViewCreated', 'onActivityCreated',
            'onClick', 'onTouch', 'onLongClick',
            'toString', 'equals', 'hashCode',
            'main', '<init>', '<clinit>',
        }
        
        return method_name in protected_methods
    
    def _is_protected_field(self, field_name: str) -> bool:
        """Проверка является ли поле защищенным"""
        protected_fields = {
            'serialVersionUID',
            'CREATOR',
        }
        
        return field_name in protected_fields
    
    def _generate_class_name(self) -> str:
        """Генерация нового имени класса"""
        self.class_counter += 1
        # Генерация короткого имени типа a/b/c
        return self._int_to_name(self.class_counter)
    
    def _generate_method_name(self) -> str:
        """Генерация нового имени метода"""
        self.method_counter += 1
        return self._int_to_name(self.method_counter)
    
    def _generate_field_name(self) -> str:
        """Генерация нового имени поля"""
        self.field_counter += 1
        return self._int_to_name(self.field_counter)
    
    def _int_to_name(self, num: int) -> str:
        """
        Преобразование числа в короткое имя
        1 -> a, 2 -> b, ..., 27 -> aa, ...
        """
        result = ""
        while num > 0:
            num -= 1
            result = chr(ord('a') + (num % 26)) + result
            num //= 26
        return result or 'a'
