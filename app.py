from flask import Flask, render_template, request, jsonify
from FacebookMarketplaceBot import FacebookMarketplaceBot
from selenium.webdriver.chrome.options import Options as ChromeOptions
import time
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

from flask import request

@app.route('/publish', methods=['GET'])
def publish():
    try:
        # Obtener los datos del formulario de la solicitud GET
        username = request.args.get('username')
        password = request.args.get('password')
        num_publications = int(request.args.get('num_publications'))
        marca = request.args.get('marca')
        modelo = request.args.get('modelo')
        precio = request.args.get('precio')
        millaje = request.args.get('millaje')
        anio = request.args.get('anio')
        tipo = request.args.get('tipo')
        carroceria = request.args.get('carroceria')
        estado = request.args.get('estado')
        transmision = request.args.get('transmision')
        
        # Resto del código para manejar los datos...
        
        chrome_options = ChromeOptions()
        chrome_options.add_argument('--headless')  # Run Chrome in headless mode
        chrome_options.add_argument('--no-sandbox')  # Bypass OS security model
        chrome_options.add_argument('--disable-dev-shm-usage')  # Overcome limited resources in Docker
        chrome_options.binary_location = '/usr/bin/google-chrome'  # Correct Chrome binary location in Docker

        bot = FacebookMarketplaceBot(username, password, chrome_options)
        bot.login()

        options = {
            "Tipo de vehículo": tipo,
            "Año": anio,
            "Carrocería": carroceria,
            "Estado del vehículo": estado,
            "Transmisión": transmision
        }

        form_data = {
            "Marca": marca,
            "Modelo": modelo,
            "Precio": precio,
            "Millaje": millaje
        }

        upload_dir = os.path.join(app.root_path, 'uploads')

        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        photo_paths = []
        for i, photo in enumerate(request.files.getlist("image")):
            photo_filename = f"uploaded_photo_{i}.jpg"
            photo_path = os.path.join(upload_dir, photo_filename)
            photo.save(photo_path)
            photo_paths.append(photo_path)
        
        for i in range(num_publications):
            bot.complete_form(form_data, options, photo_paths)
            time.sleep(15)
            bot.click_button("Publicar")
            print(f"Publicación {i+1}/{num_publications} completada.")
            time.sleep(30)

        bot.close_browser()

        return jsonify({'message': 'Publicaciones realizadas con éxito'}), 200
    except Exception as e:
        print(f"Error en la publicación: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Lanzar el servidor WSGI con Waitress
    serve(app, host='0.0.0.0', port=5000)

