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

# Establecer la variable de entorno necesaria para Flask
ENV FLASK_APP=app.py

# Exponer el puerto en el que se ejecutará la aplicación
EXPOSE 5000

# Ejecutar la aplicación
CMD ["flask", "run", "--host=0.0.0.0"]
