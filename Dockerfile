# Usar una imagen base oficial de Python
FROM python:3.8-slim-buster

# Establecer el directorio de trabajo en /app
WORKDIR /app

# Copiar el archivo de requerimientos al contenedor
COPY requirements.txt .

# Instalar las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el directorio actual (que contiene tu aplicación) al contenedor
COPY . .

# Exponer el puerto en el que se ejecutará la aplicación
EXPOSE 5000

# Ejecutar la aplicación con Gunicorn
CMD ["gunicorn", "-c", "gunicorn_config.py", "-b", ":5000", "app:app"]
