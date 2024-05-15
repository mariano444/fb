import os
import random
import time
import cv2
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import threading

class FacebookMarketplaceBot:
    def __init__(self, username, password, chrome_options=None):
        self.username = username
        self.password = password
        if chrome_options:
            self.driver = webdriver.Chrome(options=chrome_options)
        else:
            self.driver = webdriver.Chrome()
            chrome_options = webdriver.ChromeOptions()  # Añadir esta línea si no se proporciona chrome_options
            chrome_options.add_argument("--disable-notifications")  # Bloquear las notificaciones externas
            chrome_options.add_argument("--headless")  # Ejecutar en modo headless
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--remote-debugging-port=9222")  # Añadir esta línea
            chrome_options.add_argument("--disable-gpu")  # Deshabilitar GPU
            self.wait = WebDriverWait(self.driver, 20)  # Aumentar el tiempo de espera a 20 segundos
            self.photo_counter = 0  # Contador de fotos cargadas
            self.used_locations = set()  # Conjunto para almacenar las localidades utilizadas

    def login(self):
        try:
            self.driver.get("https://www.facebook.com/")
            email_field = self.wait.until(EC.visibility_of_element_located((By.NAME, "email")))
            email_field.send_keys(self.username)
            password_field = self.driver.find_element(By.NAME, "pass")
            password_field.send_keys(self.password)
            password_field.submit()
            self.wait.until(EC.url_matches("https://www.facebook.com/?sk=h_chr"))  # Espera la carga de la página principal después del inicio de sesión
            print("Inicio de sesión exitoso.")
        except TimeoutException:
            print("Tiempo de espera agotado durante el inicio de sesión.")
        except NoSuchElementException:
            print("No se encontró el campo de correo electrónico o contraseña.")
        except Exception as e:
            print(f"Error durante el inicio de sesión: {e}")

    def complete_form(self, form_data, options, uploaded_photos):
        try:
            self.driver.get("https://www.facebook.com/marketplace/create/vehicle")
            print("Redireccionado a Marketplace.")

            for category, option in options.items():
                self.select_option(category, option)

            for field_name, value in form_data.items():
                field = self.find_field_by_keyword(field_name)
                if field:
                    field.clear()  # Limpiar el campo antes de escribir
                    field.send_keys(value)
                    print(f"Campo '{field_name}' completado automáticamente con '{value}'.")
                else:
                    print(f"No se encontró el campo '{field_name}'.")

            # Llenar la descripción
            description = input("Ingrese la descripción del vehículo: ")
            self.fill_description(description)

            # Obtener el nombre de una localidad aleatoria dentro de Argentina
            location_name = self.get_random_location_name()
            if location_name:
                print(f"Ubicación seleccionada: {location_name}")

                # Encuentra el campo de ubicación y lo completa con el nombre obtenido
                location_field = self.find_field_by_keyword("Ubicación")
                if location_field:
                    location_field.clear()  # Limpiar el campo antes de escribir
                    location_field.send_keys(Keys.CONTROL + "a")  # Seleccionar todo el texto actual
                    location_field.send_keys(Keys.DELETE)  # Eliminar el texto seleccionado
                    location_field.send_keys(location_name)
                    print(f"Ubicación '{location_name}' establecida en el campo.")
                    # Hacer clic en el primer resultado después de colocar la ubicación
                    self.click_first_location_result()

            # Subir fotos desde las rutas proporcionadas
            self.upload_photos_from_list(uploaded_photos)

            # Hacer clic en el botón "Siguiente"
            self.click_button("Siguiente")

        except TimeoutException:
            print("Tiempo de espera agotado durante la carga de Marketplace.")
        except NoSuchElementException:
            print("No se encontró el campo necesario en el formulario.")
        except Exception as e:
            print(f"Error al completar el formulario: {e}")

    def upload_photos_from_list(self, uploaded_photos):
        try:
            uploaded_paths = set()  # Mantener un registro de las imágenes ya cargadas
            uploaded_paths.add("")  # Agregar un elemento vacío al conjunto para la primera carga
            for _ in range(len(uploaded_photos)):  # Realizar tantas iteraciones como fotos proporcionadas
                photo_path = random.choice(uploaded_photos)  # Seleccionar una foto aleatoria de la lista
                while photo_path in uploaded_paths:  # Si la foto ya ha sido cargada, seleccionar otra
                    photo_path = random.choice(uploaded_photos)
                input_field = self.driver.find_element(By.XPATH, "//input[@type='file']")
                input_field.send_keys(photo_path)
                print(f"Fotografía {photo_path} cargada.")
                uploaded_paths.add(photo_path)  # Registrar la imagen cargada
                time.sleep(1)  # Esperar un segundo entre la carga de cada foto
                self.driver.execute_script('arguments[0].value=""', input_field)
        except Exception as e:
            print(f"Error al cargar las fotos desde la lista proporcionada: {e}")

    def find_field_by_keyword(self, keyword):
        try:
            field = self.driver.find_element(By.XPATH, f"//*[contains(text(), '{keyword}')]/following::input[1]")
            return field
        except NoSuchElementException:
            return None

    def fill_description(self, description):
        try:
            description_field = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "textarea.x1i10hfl")))
            description_field.clear()  # Limpiar el campo antes de escribir
            description_field.send_keys(description)  # Completa el campo con la descripción proporcionada
            print("Descripción completada automáticamente.")
        except TimeoutException:
            print("Tiempo de espera agotado para el campo de descripción.")
        except Exception as e:
            print(f"Error al completar la descripción: {e}")

    def select_option(self, category, option):
        try:
            label_element = self.wait.until(EC.visibility_of_element_located((By.XPATH, f"//label[contains(@aria-label, '{category}')]")))
            self.driver.execute_script(
                "arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'center' });",
                label_element)  # Desplazar la vista hacia la etiqueta del campo

            self.driver.execute_script("arguments[0].click();",
                                       label_element)  # Hacer clic en el label para desplegar las opciones

            option_element = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, f"//span[text()='{option}']")))
            self.driver.execute_script(
                "arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'center' });",
                option_element)  # Desplazar la vista hacia la opción
            time.sleep(1)  # Esperar un segundo para asegurar el desplazamiento completo

            action = ActionChains(self.driver)
            action.move_to_element(option_element).click().perform()  # Hacer clic en la opción después de enfocar la vista
            print(f"Opción '{option}' seleccionada en '{category}'.")

        except TimeoutException:
            print(f"No se pudo encontrar la opción '{option}' en '{category}'.")
        except Exception as e:
            print(f"Error al seleccionar la opción '{option}' en '{category}': {e}")

    def get_random_location_name(self):
        try:
            # Cargar las localidades desde el archivo localidades.py
            from localidades import localidades_argentinas

            # Obtener una localidad aleatoria dentro de Argentina que no haya sido utilizada
            if localidades_argentinas:
                available_locations = set(localidades_argentinas) - self.used_locations
                if available_locations:
                    location_name = random.choice(list(available_locations))
                    self.used_locations.add(location_name)
                    return location_name
                else:
                    raise Exception("Todas las localidades han sido utilizadas.")
            else:
                raise Exception("No se encontraron localidades dentro de Argentina.")
        except Exception as e:
            print(f"Error al obtener el nombre de la ubicación aleatoria: {e}")
            return None

    def click_button(self, button_text):
        try:
            button = self.wait.until(EC.element_to_be_clickable((By.XPATH, f"//span[text()='{button_text}']")))
            self.driver.execute_script("arguments[0].scrollIntoView();", button)
            time.sleep(2)  # Esperar 2 segundos antes de hacer clic
            button.click()
            print(f"Botón '{button_text}' clicado.")
        except TimeoutException:
            print(f"No se pudo encontrar el botón '{button_text}'.")
        except Exception as e:
            print(f"Error al hacer clic en el botón '{button_text}': {e}")

    def close_browser(self):
        self.driver.quit()
        print("Navegador cerrado.")

    def upload_photos_from_folder(self, folder_name, modified_folder_name, max_photos=10):
        try:
            folder_path = os.path.join(os.getcwd(), folder_name)
            modified_folder_path = os.path.join(os.getcwd(), modified_folder_name)
            if not os.path.exists(modified_folder_path):
                os.makedirs(modified_folder_path)
            photos = os.listdir(folder_path)
            random.shuffle(photos)  # Aleatorizar el orden de las fotos
            num_photos_to_upload = min(max_photos, len(photos))  # Cargar un máximo de `max_photos` fotos
            photo_count = 0  # Contador de fotos cargadas
            for index, photo in enumerate(photos):
                if photo_count >= num_photos_to_upload:
                    break  # Detener la carga si se han cargado suficientes fotos
                photo_path = os.path.join(folder_path, photo)
                modified_photo_path = os.path.join(modified_folder_path, f"modified_{photo}")
                if index == 0:  # Solo modificar la primera foto
                    self.modify_and_save_photo(photo_path, modified_photo_path)
                else:
                    modified_photo_path = photo_path  # No modificar las otras fotos
                input_field = self.driver.find_element(By.XPATH, "//input[@type='file']")
                input_field.send_keys(modified_photo_path)
                print(f"Fotografía {photo} cargada.")
                photo_count += 1  # Incrementar el contador de fotos cargadas
                time.sleep(1)  # Esperar un segundo entre la carga de cada foto
                # Eliminar la foto después de cargarla
                photos.remove(photo)
                self.driver.execute_script('arguments[0].value=""', input_field)
        except Exception as e:
            print(f"Error al cargar las fotos: {e}")

    def modify_and_save_photo(self, original_path, modified_path):
        try:
            original_image = cv2.imread(original_path)
            if original_image is None:
                raise FileNotFoundError(f"No se pudo leer la imagen: {original_path}")
            
            # Aplicar un filtro aleatorio en alta definición
            modified_image = self.apply_random_hd_filter(original_image)

            # Agregar elementos aleatorios
            modified_image = self.add_random_element(modified_image)

            # Agregar texto aleatorio
            modified_image = self.add_random_text(modified_image)

            # Realizar diseño profesional
            modified_image = self.apply_professional_design(modified_image)

            # Guardar la imagen modificada
            cv2.imwrite(modified_path, modified_image)
        except Exception as e:
            print(f"Error al modificar y guardar la imagen: {e}")

    def add_random_element(self, image):
        try:
            elements_folder = "elements"
            elements_path = os.path.join(os.getcwd(), elements_folder)
            icons = [file for file in os.listdir(elements_path) if file.endswith('.png')]
            icons_images = []
            for icon in icons:
                icon_path = os.path.join(elements_path, icon)
                icon_img = cv2.imread(icon_path, cv2.IMREAD_UNCHANGED)
                if icon_img is not None:
                    # Convertir la imagen a 3 canales (RGB) si tiene 4 canales (RGBA)
                    if icon_img.shape[2] == 4:
                        icon_img = cv2.cvtColor(icon_img, cv2.COLOR_RGBA2RGB)
                    icons_images.append(icon_img)
            
            if not icons_images:
                raise FileNotFoundError("No se encontraron imágenes PNG en la carpeta 'elements'.")

            # Número aleatorio de elementos a agregar (entre 1 y 4)
            num_elements = random.randint(1, 1)
            for _ in range(num_elements):
                random_icon = random.choice(icons_images)
                # Calcular un tamaño aleatorio para el elemento
                element_height, element_width = random_icon.shape[:2]
                resize_factor = random.uniform(0.2, 0.3)  # Factor de escala aleatorio
                new_height = int(element_height * resize_factor)
                new_width = int(element_width * resize_factor)
                random_icon_resized = cv2.resize(random_icon, (new_width, new_height))
                image = self.paste_element(image, random_icon_resized)

            return image
        except Exception as e:
            print(f"Error al agregar elementos aleatorios: {e}")
            return image

    def paste_element(self, image, element):
        try:
            # Obtener las dimensiones de la imagen y el elemento
            image_height, image_width, _ = image.shape
            element_height, element_width, _ = element.shape

            # Calcular las posiciones aleatorias donde se pegará el elemento
            x_position = random.randint(0, image_width - element_width)
            y_position = random.randint(0, image_height - element_height)

            # Pegar el elemento en la imagen
            image[y_position:y_position + element_height, x_position:x_position + element_width] = element

            return image
        except Exception as e:
            print(f"Error al pegar el elemento: {e}")
            return image

    def add_random_text(self, image):
        try:
            # Obtener una lista de textos aleatorios
            random_texts = [
                "¡Gran oferta!",
                "¡Descuentos increíbles!",
                "¡Promoción especial!",
                "¡Precios bajos!",
                "¡Aprovecha ahora!"
            ]

            # Seleccionar un texto aleatorio de la lista
            text = random.choice(random_texts)

            # Establecer la fuente, tamaño y color del texto
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 1
            font_color = (255, 255, 255)  # Color blanco
            thickness = 2

            # Obtener las dimensiones de la imagen
            image_height, image_width, _ = image.shape

            # Establecer la posición aleatoria donde se colocará el texto
            x_position = random.randint(0, image_width - 10 * len(text))  # Ajuste aproximado para la longitud del texto
            y_position = random.randint(50, image_height - 50)  # Altura aleatoria dentro del rango

            # Dibujar el texto en la imagen
            cv2.putText(image, text, (x_position, y_position), font, font_scale, font_color, thickness)

            return image
        except Exception as e:
            print(f"Error al agregar texto aleatorio: {e}")
            return image

    def apply_professional_design(self, image):
        try:
            # Aplicar un marco decorativo alrededor de la imagen
            border_size = 50
            border_color = (0, 0, 0)  # Color negro
            image_height, image_width, _ = image.shape
            image_with_border = cv2.copyMakeBorder(image, border_size, border_size, border_size, border_size,
                                                    cv2.BORDER_CONSTANT, value=border_color)

            # Agregar un título a la imagen
            title = "OFERTA ESPECIAL"
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 2
            font_color = (255, 255, 255)  # Color blanco
            thickness = 3
            text_size = cv2.getTextSize(title, font, font_scale, thickness)[0]
            text_x = int((image_width + 2 * border_size - text_size[0]) / 2)
            text_y = border_size - 10  # Ajuste fino de la posición vertical
            cv2.putText(image_with_border, title, (text_x, text_y), font, font_scale, font_color, thickness)

            return image_with_border
        except Exception as e:
            print(f"Error al aplicar el diseño profesional: {e}")
            return image

    def apply_random_hd_filter(self, image):
        try:
            filters_folder = "filters"
            filters_path = os.path.join(os.getcwd(), filters_folder)
            filters = [file for file in os.listdir(filters_path) if file.endswith('.png')]
            if not filters:
                raise FileNotFoundError("No se encontraron imágenes PNG en la carpeta 'filters'.")

            random_filter = random.choice(filters)
            filter_path = os.path.join(filters_path, random_filter)
            hd_filter = cv2.imread(filter_path, cv2.IMREAD_UNCHANGED)

            if hd_filter.shape[2] == 4:
                hd_filter = cv2.cvtColor(hd_filter, cv2.COLOR_RGBA2RGB)

            # Cambiar el tamaño del filtro para que coincida con el tamaño de la imagen
            hd_filter_resized = cv2.resize(hd_filter, (image.shape[1], image.shape[0]))

            # Mezclar la imagen original con el filtro
            alpha = 0.6  # Peso de la imagen original
            beta = 1.0 - alpha  # Peso del filtro
            blended_image = cv2.addWeighted(image, alpha, hd_filter_resized, beta, 0.0)

            return blended_image
        except Exception as e:
            print(f"Error al aplicar el filtro HD: {e}")
            return image

    def click_first_location_result(self):
        try:
            # Esperar a que aparezca la lista de resultados de ubicación
            location_results = self.wait.until(EC.visibility_of_all_elements_located((By.XPATH, "//ul[contains(@role,'listbox')]//li")))

            # Hacer clic en el primer elemento de la lista si hay resultados
            if location_results:
                location_results[0].click()
                print("Se hizo clic en el primer resultado de ubicación.")
            else:
                print("No se encontraron resultados de ubicación.")
        except TimeoutException:
            print("Tiempo de espera agotado para los resultados de ubicación.")
        except Exception as e:
            print(f"Error al hacer clic en el primer resultado de ubicación: {e}")


if __name__ == "__main__":
    # Solicitar credenciales de inicio de sesión
    username = input("Ingrese su correo electrónico: ")
    password = input("Ingrese su contraseña: ")
    num_publications = int(input("Ingresa el número de publicaciones que deseas hacer: "))

    # Establecer las opciones del formulario una vez fuera del bucle
    options = {}

    # Solicitar los datos del formulario una vez fuera del bucle
    form_data = {}

    bot = FacebookMarketplaceBot(username, password)
    bot.login()

    for i in range(num_publications):
        # Pasar los datos del formulario a la función complete_form() dentro del bucle
        bot.complete_form(form_data, options)
    
        time.sleep(15)  # Esperar 15 segundos antes de proceder
        bot.click_button("Publicar")
        print(f"Publicación {i+1}/{num_publications} completada.")
        time.sleep(30)  # Esperar 30 segundos entre publicaciones

    bot.close_browser()
