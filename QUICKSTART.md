# 🚀 Быстрый старт

## Минимальная установка (5 минут)

### 1. Установка зависимостей

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

# Установка Android SDK
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

### 2. Запуск сервиса

```bash
cd apk_protection_service
pip3 install -r requirements.txt
./start.sh
```

### 3. Использование

Откройте браузер: `http://localhost:5000`

## Docker (рекомендуется)

```bash
# Сборка образа
docker-compose build

# Запуск сервиса
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down
```

## Быстрый тест через API

```bash
# Health check
curl http://localhost:5000/api/health

# Обработка APK
curl -X POST http://localhost:5000/api/process \
  -F "file=@your_app.apk" \
  -o protected_app.apk
```

## Типичные проблемы

### Java не найдена
```bash
sudo apt install -y openjdk-17-jdk
```

### apktool не найден
```bash
apktool --version
# Если ошибка - переустановите apktool
```

### Port 5000 занят
```bash
# Измените порт в app.py:
# app.run(host='0.0.0.0', port=5001)
```

### Ошибка при декомпиляции
- Проверьте что APK файл не поврежден
- Убедитесь что это валидный APK файл

## Следующие шаги

1. Прочитайте полную документацию в `README.md`
2. Изучите архитектуру в `service_architecture.md`
3. Настройте конфигурацию в `config.py`

---

**Нужна помощь?** Проверьте логи в `temp/app.log`
