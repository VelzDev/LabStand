# Установка и запуск

## Требования
- Python 3.11+
- Git
- Виртуальное окружение (venv)

## Установка
1. **Склонируйте репозиторий:**
   ```sh
   git clone https://github.com/VelzDev/LabStand.git
   cd <ИМЯ_ПАПКИ_ПРОЕКТА>
   ```
2. **Создайте и активируйте виртуальное окружение:**
   ```sh
   python -m venv venv
   # Для Windows:
   venv\\Scripts\\activate
   # Для macOS/Linux:
   source venv/bin/activate
   ```
3. **Установите зависимости:**
   ```sh
   pip install -r requirements.txt
   ```

## Запуск
```sh
python simulator.py
```

## Структура проекта
```
<ИМЯ_ПАПКИ_ПРОЕКТА>/
│── bin/
│   ├── images/      # Картинки для симуляции
│   ├── ... (другие файлы)
│── simulator.py     # Главный файл приложения
│── requirements.txt # Зависимости проекта
│── README.md        # Документация
```

