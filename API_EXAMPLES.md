# 📡 API Examples

## Базовые запросы

### Health Check

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

### Информация о сервисе

```bash
curl http://localhost:5000/api/info
```

**Ответ:**
```json
{
  "service": "APK Protection Service",
  "version": "1.0.0",
  "description": "Сервис для защиты и обфускации Android APK файлов",
  "features": [
    "Удаление чувствительных разрешений",
    "Обновление targetSdkVersion",
    "Обфускация кода (классы, методы, поля)",
    "Шифрование строковых констант",
    "Обфускация манифеста",
    "Новая подпись APK"
  ],
  "max_file_size_mb": 150,
  "supported_formats": [".apk"]
}
```

## Обработка APK

### Базовая обработка (все опции по умолчанию)

```bash
curl -X POST http://localhost:5000/api/process \
  -F "file=@my_app.apk" \
  -o protected_app.apk
```

### С кастомными опциями

```bash
curl -X POST http://localhost:5000/api/process \
  -F "file=@my_app.apk" \
  -F 'options={"remove_sensitive_permissions":true,"update_target_sdk":true,"obfuscate_code":true,"obfuscate_manifest":true}' \
  -o protected_app.apk
```

### Только удаление разрешений

```bash
curl -X POST http://localhost:5000/api/process \
  -F "file=@my_app.apk" \
  -F 'options={"remove_sensitive_permissions":true,"update_target_sdk":false,"obfuscate_code":false,"obfuscate_manifest":false}' \
  -o protected_app.apk
```

### Только обфускация

```bash
curl -X POST http://localhost:5000/api/process \
  -F "file=@my_app.apk" \
  -F 'options={"remove_sensitive_permissions":false,"update_target_sdk":false,"obfuscate_code":true,"obfuscate_manifest":true}' \
  -o protected_app.apk
```

## Python примеры

### Использование requests

```python
import requests

# Health check
response = requests.get('http://localhost:5000/api/health')
print(response.json())

# Обработка APK
with open('my_app.apk', 'rb') as f:
    files = {'file': f}
    options = {
        'remove_sensitive_permissions': True,
        'update_target_sdk': True,
        'obfuscate_code': True,
        'obfuscate_manifest': True
    }
    data = {'options': str(options)}
    
    response = requests.post(
        'http://localhost:5000/api/process',
        files=files,
        data=data
    )
    
    if response.status_code == 200:
        with open('protected_app.apk', 'wb') as out:
            out.write(response.content)
        print("APK успешно обработан!")
    else:
        print(f"Ошибка: {response.json()}")
```

### Асинхронная обработка

```python
import aiohttp
import asyncio

async def process_apk(apk_path, output_path):
    async with aiohttp.ClientSession() as session:
        with open(apk_path, 'rb') as f:
            data = aiohttp.FormData()
            data.add_field('file', f, filename='app.apk')
            data.add_field('options', '{"obfuscate_code":true}')
            
            async with session.post(
                'http://localhost:5000/api/process',
                data=data
            ) as response:
                if response.status == 200:
                    content = await response.read()
                    with open(output_path, 'wb') as out:
                        out.write(content)
                    print("Готово!")
                else:
                    error = await response.json()
                    print(f"Ошибка: {error}")

# Запуск
asyncio.run(process_apk('my_app.apk', 'protected_app.apk'))
```

## JavaScript примеры

### Fetch API

```javascript
// Health check
fetch('http://localhost:5000/api/health')
  .then(response => response.json())
  .then(data => console.log(data));

// Обработка APK
const fileInput = document.getElementById('fileInput');
const file = fileInput.files[0];

const formData = new FormData();
formData.append('file', file);
formData.append('options', JSON.stringify({
  remove_sensitive_permissions: true,
  update_target_sdk: true,
  obfuscate_code: true,
  obfuscate_manifest: true
}));

fetch('http://localhost:5000/api/process', {
  method: 'POST',
  body: formData
})
  .then(response => response.blob())
  .then(blob => {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'protected_app.apk';
    a.click();
  });
```

### Axios

```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

// Обработка APK
const form = new FormData();
form.append('file', fs.createReadStream('my_app.apk'));
form.append('options', JSON.stringify({
  obfuscate_code: true,
  obfuscate_manifest: true
}));

axios.post('http://localhost:5000/api/process', form, {
  headers: form.getHeaders(),
  responseType: 'arraybuffer'
})
  .then(response => {
    fs.writeFileSync('protected_app.apk', response.data);
    console.log('APK обработан!');
  })
  .catch(error => {
    console.error('Ошибка:', error.response.data);
  });
```

## Обработка ошибок

### Коды ответов

- `200` - Успешная обработка
- `400` - Неверный запрос (нет файла, неверный формат)
- `413` - Файл слишком большой (>150 MB)
- `500` - Внутренняя ошибка сервера

### Примеры ошибок

**Файл не предоставлен:**
```json
{
  "error": "No file provided"
}
```

**Неверный формат:**
```json
{
  "error": "Invalid file format. Only .apk files are supported"
}
```

**Ошибка обработки:**
```json
{
  "error": "Failed to process APK: <detailed error message>"
}
```

## Batch обработка

### Обработка нескольких APK

```python
import requests
import os

def process_apk_batch(apk_files, output_dir):
    for apk_file in apk_files:
        print(f"Processing {apk_file}...")
        
        with open(apk_file, 'rb') as f:
            files = {'file': f}
            response = requests.post(
                'http://localhost:5000/api/process',
                files=files
            )
            
            if response.status_code == 200:
                output_path = os.path.join(
                    output_dir, 
                    f"protected_{os.path.basename(apk_file)}"
                )
                with open(output_path, 'wb') as out:
                    out.write(response.content)
                print(f"✅ {apk_file} -> {output_path}")
            else:
                print(f"❌ {apk_file}: {response.json()['error']}")

# Использование
apk_files = ['app1.apk', 'app2.apk', 'app3.apk']
process_apk_batch(apk_files, 'output/')
```

## Мониторинг

### Проверка статуса

```bash
#!/bin/bash

while true; do
  STATUS=$(curl -s http://localhost:5000/api/health | jq -r '.status')
  echo "$(date): Service status: $STATUS"
  sleep 60
done
```

### Логирование

```python
import requests
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def process_with_logging(apk_path):
    logging.info(f"Starting processing: {apk_path}")
    
    try:
        with open(apk_path, 'rb') as f:
            response = requests.post(
                'http://localhost:5000/api/process',
                files={'file': f}
            )
        
        if response.status_code == 200:
            logging.info(f"Successfully processed: {apk_path}")
            return response.content
        else:
            logging.error(f"Failed to process: {response.json()}")
            return None
            
    except Exception as e:
        logging.error(f"Exception: {e}")
        return None
```

---

**Больше примеров?** Проверьте `frontend/js/app.js` для полного примера веб-интерфейса.
