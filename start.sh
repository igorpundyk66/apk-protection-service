#!/bin/bash

# APK Protection Service - Start Script

echo "🚀 Starting APK Protection Service..."

# Проверка зависимостей
echo "📋 Checking dependencies..."

# Java
if ! command -v java &> /dev/null; then
    echo "❌ Java not found. Please install OpenJDK 17+"
    exit 1
fi
echo "✅ Java: $(java -version 2>&1 | head -n 1)"

# apktool
if ! command -v apktool &> /dev/null; then
    echo "❌ apktool not found. Please install apktool 2.9.3+"
    exit 1
fi
echo "✅ apktool: $(apktool --version 2>&1 | head -n 1)"

# apksigner
if ! command -v apksigner &> /dev/null; then
    echo "❌ apksigner not found. Please install Android SDK Build Tools"
    exit 1
fi
echo "✅ apksigner: $(apksigner --version)"

# zipalign
if ! command -v zipalign &> /dev/null; then
    echo "❌ zipalign not found. Please install Android SDK Build Tools"
    exit 1
fi
echo "✅ zipalign: OK"

# Python packages
echo "📦 Checking Python packages..."
python3 -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Flask not found. Installing dependencies..."
    pip3 install -r requirements.txt
fi
echo "✅ Python packages: OK"

# Создание директорий
echo "📁 Creating directories..."
mkdir -p temp/uploads temp/working temp/output temp/keystore
echo "✅ Directories created"

# Запуск сервиса
echo ""
echo "🎯 Starting Flask server..."
echo "📍 Service will be available at: http://localhost:5000"
echo "📍 API documentation: http://localhost:5000/api/info"
echo ""
echo "Press Ctrl+C to stop the service"
echo ""

python3 app.py
