import requests
from PIL import Image
from io import BytesIO
import pyttsx3
import pyaudio
import json
import re
import os
from vosk import Model, KaldiRecognizer

# Загружаем модель распознавания речи Vosk
model = Model("vosk-model-small-en-us-0.15")

# Создаем распознаватель
rec = KaldiRecognizer(model, 16000)

# Инициализируем библиотеку pyttsx3 для синтеза речи
engine = pyttsx3.init()

current_image = None

# Функция для выполнения команды "показать"
def show_image():
    response = requests.get("https://dog.ceo/api/breeds/image/random")
    data = json.loads(response.text)
    image_url = data["message"]

    # Загрузка изображения из URL
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))

    # Отображение изображения
    img.show()

# Функция для выполнения команды "сохранить"
def save_image():
    response = requests.get("https://dog.ceo/api/breeds/image/random")
    data = json.loads(response.text)
    image_url = data["message"]

    # Загрузка изображения из URL
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))

    # Получение имени файла из URL
    filename = os.path.basename(image_url)

    # Сохранение изображения
    img.save(filename)

    print(f"Изображение сохранено как {filename}")

# Функция для выполнения команды "следующая"
def next_image():
    global current_image

    response = requests.get("https://dog.ceo/api/breeds/image/random")
    data = json.loads(response.text)
    image_url = data["message"]

    # Загрузка изображения из URL
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))

    # Закрытие предыдущего изображения, если оно существует
    if current_image is not None:
        current_image.close()

    # Обновление текущего изображения
    current_image = img

    # Отображение изображения
    current_image.show()

# Функция для выполнения команды "назвать породу"
def get_breed():
    response = requests.get("https://dog.ceo/api/breeds/image/random")
    data = json.loads(response.text)
    image_url = data["message"]

    # Извлечение названия породы из текста ссылки
    breed_name = re.search(r"breeds/(\w+)/", image_url).group(1)

    print(f"Название породы: {breed_name}")

# Функция для выполнения команды "разрешение"
def get_resolution():
    response = requests.get("https://dog.ceo/api/breeds/image/random")
    data = json.loads(response.text)
    image_url = data["message"]

    # Загрузка изображения из URL
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))

    # Получение разрешения изображения
    width, height = img.size

    print(f"Разрешение изображения: {width}x{height}")

# Функция для обработки распознанной команды
def process_command(command):
    print(command)
    if "show" in command.strip():
        show_image()
    elif "save" in command.strip():
        save_image()
    elif "next" in command.strip():
        next_image()
    elif "breed" in command.strip():
        get_breed()
    elif "resolution" in command.strip():
        get_resolution()
    else:
        print("Не распознана команда.")

# Основной цикл прослушивания и распознавания речи
stream = pyaudio.PyAudio().open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
stream.start_stream()

print("Голосовой ассистент готов к работе.")

while True:

    data = stream.read(8192)
    if len(data) == 0:
        break
    if rec.AcceptWaveform(data):
        result = json.loads(rec.Result())
        if "text" in result:
            command = result["text"]
            process_command(command)


# Завершение работы ассистента
stream.stop_stream()
stream.close()
