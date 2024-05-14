from flask import Flask, render_template, request, jsonify
from FacebookMarketplaceBot import FacebookMarketplaceBot
import time
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('https://fb-tz4k.onrender.com/publish', methods=['POST'])
def publish():
    try:
        username = request.form.get('username')
        password = request.form.get('password')
        num_publications = int(request.form.get('num_publications'))
        marca = request.form['marca']
        modelo = request.form['modelo']
        precio = request.form['precio']
        millaje = request.form['millaje']
        anio = request.form['anio']
        tipo = request.form['tipo']
        carroceria = request.form['carroceria']
        estado = request.form['estado']
        transmision = request.form['transmision']
        
        bot = FacebookMarketplaceBot(username, password)
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

        # Directorio donde guardar las imágenes
        upload_dir = os.path.join(app.root_path, 'uploads')

        # Crear el directorio si no existe
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        # Upload photos
        photo_paths = []
        for i, photo in enumerate(request.files.getlist("image")):
            # Generar un nombre de archivo único para cada foto
            photo_filename = f"uploaded_photo_{i}.jpg"
            photo_path = os.path.join(upload_dir, photo_filename)
            photo.save(photo_path)
            photo_paths.append(photo_path)
        
        for i in range(num_publications):
            bot.complete_form(form_data, options, photo_paths)
            time.sleep(15)  # Esperar 15 segundos antes de proceder
            bot.click_button("Publicar")
            print(f"Publicación {i+1}/{num_publications} completada.")
            time.sleep(30)  # Esperar 30 segundos entre publicaciones

        bot.close_browser()

        return jsonify({'message': 'Publicaciones realizadas con éxito'}), 200
    except Exception as e:
        print(f"Error en la publicación: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Lanzar el servidor WSGI con Waitress
    serve(app, host='0.0.0.0', port=5000)
