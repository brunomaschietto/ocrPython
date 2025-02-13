from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import pytesseract
from pdf2image import convert_from_path
import os
import unicodedata

app = Flask(__name__)
CORS(app) 

def normalize_text(text):
    return unicodedata.normalize('NFKD', text)

def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    return binary

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/extract_text', methods=['POST'])
def extract_text():
    file = request.files['pdf']
    file.save('input.pdf')

    images = convert_from_path('input.pdf', 500, poppler_path=r'C:\Program Files\poppler-24.02.0\Library\bin')
    pytesseract.pytesseract.tesseract_cmd = "C:\Program Files\Tesseract-OCR\Tesseract.exe"

    pages_text = []

    tessdata_dir_config = r'--tessdata-dir "C:\Program Files\Tesseract-OCR\tessdata"'
    config = r'--oem 3 --psm 6 ' + tessdata_dir_config

    for i in range(len(images)):
        image_path = 'page' + str(i) + '.jpg'
        images[i].save(image_path, 'JPEG')

        image = cv2.imread(image_path)
        processed_image = preprocess_image(image)

        text = pytesseract.image_to_string(processed_image, config=config, lang='por')
        normalized_text = normalize_text(text)
        pages_text.append(normalized_text)

        try:
            os.remove(image_path)
            print(f"Imagem {image_path} apagada com sucesso.")
        except OSError as e:
            print(f"Erro ao apagar a imagem {image_path}: {e}")

    os.remove('input.pdf')
    full_text = ' '.join(pages_text)
    tamanho = len(full_text)

    return jsonify({'text': full_text, 'tamanho': tamanho})

if __name__ == '__main__':
    app.run(debug=True)