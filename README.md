# APK Protection Service 🛡️

Сервис для защиты и обфускации Android APK файлов с целью обхода Google Play Protect и других систем безопасности при sideloading.

## 🎯 Возможности

- ✅ **Удаление чувствительных разрешений** - Автоматическое удаление триггерных permissions (SMS, Accessibility, Notification Listener)
- ✅ **Обновление targetSdkVersion** - Обновление до актуальной версии Android SDK (API 33+)
- ✅ **Обфускация кода** - Переименование классов, методов и полей в Smali коде
- ✅ **Обфускация манифеста** - Изменение структуры AndroidManifest.xml
- ✅ **Удаление отладочной информации** - Очистка debug директив из Smali
- ✅ **Автоматическая подпись** - Генерация keystore и подпись APK
- ✅ **Веб-интерфейс** - Удобный drag-and-drop интерфейс для загрузки файлов

## 🏗️ Архитектура

```
apk_protection_service/
├── app.py                      # Главное Flask приложение
├── config.py                   # Конфигурация
├── requirements.txt            # Python зависимости
├── api/
│   └── routes.py               # API endpoints
├── core/
│   ├── analyzer.py             # Анализ APK
│   ├── decompiler.py           # Декомпиляция (apktool)
│   ├── manifest_modifier.py    # Модификация манифеста
│   ├── obfuscator.py           # Обфускация кода
│   ├── rebuilder.py            # Пересборка APK
│   ├── signer.py               # Подпись APK
│   └── pipeline.py             # Главный pipeline
├── utils/
│   ├── file_manager.py         # Управление файлами
│   └── helpers.py              # Вспомогательные функции
├── frontend/
│   ├── index.html              # Веб-интерфейс
│   ├── css/styles.css          # Стили
│   └── js/app.js               # JavaScript логика
└── temp/                       # Временные файлы
    ├── uploads/                # Загруженные APK
    ├── working/                # Рабочие директории
    └── output/                 # Обработанные APK
```

## 📋 Требования

### Системные зависимости

- **Python 3.11+**
- **Java 17+** (OpenJDK)
- **apktool 2.9.3+**
- **Android SDK Build Tools 34.0.0+** (для apksigner и zipalign)

### Python пакеты

- Flask 3.0.0
- Werkzeug 3.0.1

## 🚀 Установка

### 1. Установка системных зависимостей

```bash
# Обновление системы
sudo apt update

# Установка Java
sudo apt install -y openjdk-17-jdk openjdk-17-jre

# Установка apktool
cd /tmp
wget https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/linux/apktool -O apktool
wget https://bitbucket.org/iBotPeaches/apktool/downloads/apktool_2.9.3.jar -O apktool.jar
chmod +x apktool
sudo mv apktool /usr/local/bin/
sudo mv apktool.jar /usr/local/bin/

# Установка Android SDK Command Line Tools
wget https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip
unzip commandlinetools-linux-11076708_latest.zip
mkdir -p ~/android-sdk/cmdline-tools
mv cmdline-tools ~/android-sdk/cmdline-tools/latest

# Установка build-tools
export ANDROID_HOME=~/android-sdk
yes | ~/android-sdk/cmdline-tools/latest/bin/sdkmanager --licenses
~/android-sdk/cmdline-tools/latest/bin/sdkmanager "build-tools;34.0.0" "platform-tools"

# Создание символических ссылок
sudo ln -sf ~/android-sdk/build-tools/34.0.0/apksigner /usr/local/bin/apksigner
sudo ln -sf ~/android-sdk/build-tools/34.0.0/zipalign /usr/local/bin/zipalign
```

### 2. Установка сервиса

```bash
# Клонирование/копирование проекта
cd /path/to/apk_protection_service

# Установка Python зависимостей
pip3 install -r requirements.txt
```

### 3. Запуск сервиса

```bash
# Запуск в режиме разработки
python3 app.py

# Сервис будет доступен по адресу: http://localhost:5000
```

## 🎮 Использование

### Веб-интерфейс

1. Откройте браузер и перейдите по адресу `http://localhost:5000`
2. Перетащите APK файл в область загрузки или нажмите "Выбрать файл"
3. Выберите опции обработки (все включены по умолчанию)
4. Нажмите "Обработать APK"
5. Дождитесь завершения обработки (может занять несколько минут)
6. Скачайте защищенный APK файл

### API

#### Health Check

```bash
curl http://localhost:5000/api/health
```

**Ответ:**
```json
{
  "status": "healthy",
  "service": "APK Protection Service",
  "version": "1.0.0"
}
```

#### Информация о сервисе

```bash
curl http://localhost:5000/api/info
```

**Ответ:**
```json
{
  "service": "APK Protection Service",
  "version": "1.0.0",
  "description": "Сервис для защиты и обфускации Android APK файлов",
  "features": [...],
  "max_file_size_mb": 150,
  "supported_formats": [".apk"]
}
```

#### Обработка APK

```bash
curl -X POST http://localhost:5000/api/process \
  -F "file=@/path/to/your/app.apk" \
  -F 'options={"remove_sensitive_permissions":true,"update_target_sdk":true,"obfuscate_code":true,"obfuscate_manifest":true}' \
  -o protected_app.apk
```

**Параметры:**
- `file` - APK файл (обязательно)
- `options` - JSON с опциями обработки (опционально)

**Опции:**
- `remove_sensitive_permissions` (bool) - Удалить чувствительные разрешения
- `update_target_sdk` (bool) - Обновить targetSdkVersion
- `obfuscate_code` (bool) - Обфусцировать код
- `obfuscate_manifest` (bool) - Обфусцировать манифест

## 🔧 Конфигурация

Основные настройки находятся в файле `config.py`:

```python
# Максимальный размер файла
MAX_CONTENT_LENGTH = 150 * 1024 * 1024  # 150 MB

# Целевая версия SDK
DEFAULT_TARGET_SDK = 33  # Android 13

# Чувствительные разрешения для удаления
SENSITIVE_PERMISSIONS = [
    "android.permission.RECEIVE_SMS",
    "android.permission.READ_SMS",
    "android.permission.BIND_NOTIFICATION_LISTENER_SERVICE",
    "android.permission.BIND_ACCESSIBILITY_SERVICE",
    # ...
]

# Техники обфускации
OBFUSCATION_TECHNIQUES = {
    "rename_classes": True,
    "rename_methods": True,
    "rename_fields": True,
    "encrypt_strings": True,
    "obfuscate_manifest": True,
    "remove_debug_info": True,
}
```

## 📊 Pipeline обработки

1. **Анализ APK** - Извлечение информации о структуре APK
2. **Декомпиляция** - Распаковка APK с помощью apktool
3. **Модификация манифеста** - Удаление разрешений, обновление SDK, обфускация
4. **Обфускация кода** - Переименование классов/методов/полей, удаление debug info
5. **Пересборка** - Компиляция модифицированных файлов обратно в APK
6. **Подпись** - Выравнивание (zipalign) и подпись (apksigner)

## 🛡️ Методы защиты от Google Play Protect

### 1. Удаление триггерных разрешений

Google Play Protect **автоматически блокирует** sideloaded приложения с следующими разрешениями:

- `RECEIVE_SMS` / `READ_SMS` - Доступ к SMS
- `BIND_NOTIFICATION_LISTENER_SERVICE` - Доступ к уведомлениям
- `BIND_ACCESSIBILITY_SERVICE` - Accessibility сервисы

**Решение:** Сервис автоматически удаляет эти разрешения из AndroidManifest.xml.

### 2. Обновление targetSdkVersion

Приложения с устаревшим `targetSdkVersion` (более чем на 2 версии ниже текущего API) вызывают предупреждения.

**Решение:** Обновление до актуального API 33 (Android 13).

### 3. Обфускация кода

Play Protect анализирует паттерны кода для обнаружения вредоносного поведения.

**Решение:** 
- Переименование классов/методов/полей в короткие имена (a, b, c...)
- Удаление отладочной информации (.line, .local директивы)

### 4. Обфускация манифеста

**Решение:**
- Случайная перестановка элементов манифеста
- Добавление легитимных метаданных (Google Play Services, Firebase)

### 5. Новая подпись

Изменение сигнатуры приложения помогает избежать детектирования по известным подписям.

**Решение:** Генерация нового keystore и подпись APK.

## ⚠️ Ограничения

1. **Не гарантирует 100% обход** - Google постоянно обновляет алгоритмы детектирования
2. **Может сломать функциональность** - Удаление разрешений может нарушить работу приложения
3. **Упрощенная обфускация** - Для максимальной защиты рекомендуется использовать коммерческие решения (DexGuard)
4. **Только для легитимных целей** - Не используйте для распространения вредоносного ПО

## 🔍 Отладка

### Просмотр логов

```bash
tail -f temp/app.log
```

### Проверка временных файлов

```bash
ls -la temp/uploads/
ls -la temp/working/
ls -la temp/output/
```

### Тестирование отдельных компонентов

```python
from core.analyzer import APKAnalyzer
from core.decompiler import APKDecompiler

# Анализ APK
analyzer = APKAnalyzer("test.apk", "test-request")
info = analyzer.analyze()
print(info)

# Декомпиляция
decompiler = APKDecompiler("test.apk", "output_dir", "test-request")
decompiler.decompile()
```

## 📚 Дополнительные ресурсы

### Исследования

- `play_protect_triggers.md` - Детальная информация о триггерах Play Protect
- `gpp_bypass_research.md` - Исследование методов обхода Google Play Protect
- `service_architecture.md` - Подробная архитектура сервиса

### Документация

- [Apktool Documentation](https://apktool.org/)
- [Android SDK Build Tools](https://developer.android.com/tools/releases/build-tools)
- [Google Play Protect Developer Guidance](https://developers.google.com/android/play-protect/warning-dev-guidance)

## 🤝 Вклад

Проект разработан для образовательных и исследовательских целей. Используйте ответственно.

## 📝 Лицензия

Этот проект предназначен только для легитимного использования. Автор не несет ответственности за неправомерное использование.

## 🆘 Поддержка

При возникновении проблем:

1. Проверьте логи в `temp/app.log`
2. Убедитесь, что все системные зависимости установлены
3. Проверьте версии инструментов:
   ```bash
   java -version
   apktool --version
   apksigner --version
   zipalign
   ```

## 🎯 Roadmap

- [ ] Интеграция с Obfuscapk для продвинутой обфускации
- [ ] Поддержка нативных библиотек (.so)
- [ ] Шифрование строковых констант
- [ ] Обфускация потока управления
- [ ] Batch processing (обработка нескольких APK)
- [ ] REST API для интеграции с другими сервисами
- [ ] Docker контейнер для легкого развертывания

---

**Версия:** 1.0.0  
**Дата:** Октябрь 2025  
**Статус:** Production Ready ✅
