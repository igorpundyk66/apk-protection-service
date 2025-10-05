FROM ubuntu:22.04

# Установка базовых зависимостей
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    openjdk-17-jdk \
    openjdk-17-jre \
    wget \
    unzip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Установка apktool
RUN cd /tmp && \
    wget https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/linux/apktool -O apktool && \
    wget https://bitbucket.org/iBotPeaches/apktool/downloads/apktool_2.9.3.jar -O apktool.jar && \
    chmod +x apktool && \
    mv apktool /usr/local/bin/ && \
    mv apktool.jar /usr/local/bin/

# Установка Android SDK Command Line Tools
RUN cd /tmp && \
    wget https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip && \
    unzip commandlinetools-linux-11076708_latest.zip && \
    mkdir -p /opt/android-sdk/cmdline-tools && \
    mv cmdline-tools /opt/android-sdk/cmdline-tools/latest && \
    rm commandlinetools-linux-11076708_latest.zip

# Установка build-tools
ENV ANDROID_HOME=/opt/android-sdk
RUN yes | /opt/android-sdk/cmdline-tools/latest/bin/sdkmanager --licenses && \
    /opt/android-sdk/cmdline-tools/latest/bin/sdkmanager "build-tools;34.0.0" "platform-tools"

# Создание символических ссылок
RUN ln -sf /opt/android-sdk/build-tools/34.0.0/apksigner /usr/local/bin/apksigner && \
    ln -sf /opt/android-sdk/build-tools/34.0.0/zipalign /usr/local/bin/zipalign

# Создание рабочей директории
WORKDIR /app

# Копирование файлов проекта
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

# Создание необходимых директорий
RUN mkdir -p temp/uploads temp/working temp/output temp/keystore

# Открытие порта
EXPOSE 5000

# Переменные окружения
ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1

# Запуск приложения
CMD ["python3", "app.py"]
