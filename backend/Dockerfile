FROM python:3.9

# Installer les dépendances système nécessaires pour mysqlclient et mysqladmin
RUN apt-get update && apt-get install -y default-libmysqlclient-dev build-essential default-mysql-client

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Rendre le script d'initialisation exécutable
RUN chmod +x /app/scripts/docker_init.sh

EXPOSE 5000

# Utiliser un script de démarrage pour initialiser la base de données avant de démarrer l'application
CMD ["sh", "-c", "/app/scripts/docker_init.sh && gunicorn --bind 0.0.0.0:5000 --log-level debug --access-logfile - --error-logfile - wsgi:app"]