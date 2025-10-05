"""
Вспомогательные функции
"""
import subprocess
import logging
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)

def run_command(cmd: List[str], cwd: Optional[Path] = None, timeout: int = 300) -> tuple:
    """
    Выполнение команды в subprocess
    
    Args:
        cmd: Команда и аргументы
        cwd: Рабочая директория
        timeout: Таймаут в секундах
        
    Returns:
        tuple: (stdout, stderr, returncode)
        
    Raises:
        subprocess.TimeoutExpired: При превышении таймаута
        subprocess.CalledProcessError: При ненулевом коде возврата
    """
    logger.debug(f"Running command: {' '.join(cmd)}")
    if cwd:
        logger.debug(f"Working directory: {cwd}")
    
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=True
        )
        
        logger.debug(f"Command completed successfully")
        if result.stdout:
            logger.debug(f"STDOUT: {result.stdout[:500]}")  # Первые 500 символов
        
        return result.stdout, result.stderr, result.returncode
        
    except subprocess.TimeoutExpired as e:
        logger.error(f"Command timeout after {timeout}s: {' '.join(cmd)}")
        raise
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed with code {e.returncode}: {' '.join(cmd)}")
        logger.error(f"STDOUT: {e.stdout}")
        logger.error(f"STDERR: {e.stderr}")
        raise

def check_tool_installed(tool_name: str) -> bool:
    """
    Проверка установлен ли инструмент
    
    Args:
        tool_name: Имя инструмента
        
    Returns:
        bool: True если установлен
    """
    try:
        result = subprocess.run(
            ['which', tool_name],
            capture_output=True,
            text=True
        )
        installed = result.returncode == 0
        
        if installed:
            logger.debug(f"Tool '{tool_name}' is installed: {result.stdout.strip()}")
        else:
            logger.warning(f"Tool '{tool_name}' is NOT installed")
        
        return installed
        
    except Exception as e:
        logger.error(f"Error checking tool '{tool_name}': {e}")
        return False

def get_file_size_mb(file_path: Path) -> float:
    """
    Получение размера файла в МБ
    
    Args:
        file_path: Путь к файлу
        
    Returns:
        float: Размер в МБ
    """
    size_bytes = file_path.stat().st_size
    size_mb = size_bytes / (1024 * 1024)
    return round(size_mb, 2)

def ensure_dir(path: Path) -> Path:
    """
    Убедиться что директория существует
    
    Args:
        path: Путь к директории
        
    Returns:
        Path: Путь к директории
    """
    path.mkdir(parents=True, exist_ok=True)
    return path

def random_string(length: int = 8) -> str:
    """
    Генерация случайной строки
    
    Args:
        length: Длина строки
        
    Returns:
        str: Случайная строка
    """
    import random
    import string
    return ''.join(random.choices(string.ascii_lowercase, k=length))

def random_package_name() -> str:
    """
    Генерация случайного имени пакета
    
    Returns:
        str: Имя пакета в формате com.xxx.yyy
    """
    part1 = random_string(6)
    part2 = random_string(8)
    return f"com.{part1}.{part2}"
