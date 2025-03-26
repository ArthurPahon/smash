FROM python:3.9

# Installer les dépendances système nécessaires pour mysqlclient
RUN apt-get update && apt-get install -y default-libmysqlclient-dev build-essential

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]