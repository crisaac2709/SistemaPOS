# Usamos la versión exacta que tienes
FROM python:3.13.2-slim

# Evita que Python genere archivos .pyc y buferice la salida
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalamos dependencias del sistema para:
# - PostgreSQL (libpq-dev)
# - Compilación de librerías (gcc, build-essential)
# - PDFs y Imágenes (zlib, libjpeg, libfreetype6)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7-dev \
    libtiff5-dev \
    tk-dev \
    tcl-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Instalamos dependencias de Python
COPY ./requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiamos el proyecto
COPY ./ ./

# Puerto de Django
EXPOSE 8000

# Ejecución
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]