# Stage 1: Build Tailwind assets
FROM node:22 AS frontend

WORKDIR /app

# Salin konfigurasi dan file Tailwind
COPY package.json package-lock.json ./
COPY ./static/ ./static/
COPY ./templates/ ./templates/

# Install dependencies dan build Tailwind CSS
RUN npm install
RUN npm run build

# Stage 2: Django dengan Python 3.13
FROM python:3.13 AS backend

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Salin seluruh kode proyek Django
COPY . .

# Salin hasil build Tailwind dari stage frontend
COPY --from=frontend /app/static/css ./static/css

# Jalankan collectstatic
RUN python manage.py collectstatic --noinput

# Jalankan Gunicorn (ganti `project_name` dengan nama folder Django utama)
CMD ["gunicorn", "sukanews.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
