Klonowanie repo:

```bash
git clone https://github.com/ossker/docs_together.git
```
Wejdż do głownego folderu, jeżeli nie jesteś:
```bash
cd docs_togehter 
```

Zainstaluj virtualenv, jeśli nie masz:

```bash
pip install virtualenv
```

Stwórz wirtualne środowisko:
```bash
python3 -m venv env
```

Za każdym wejściem do projektu aktywuj środowisko:
```bash
env/Scripts/activate
```

Za każdym razem, gdy coś zanistalujesz w środowisku, dorzuć to do requirements.txt za pomocą tej komendy:
```bash
pip freeze > requirements.txt
```

Jeśli zapiszesz zależności w pliku requirements.txt, inni mogą łatwo odtworzyć dokładnie to samo środowisko u siebe tą komendą:
```bash
pip install -r requirements.txt
```

Uruchom serwer ASGI:
```bash
daphne docs_together.asgi:application
```

Stwórz migracje:
```bash
python manage.py makemigrations
```


```bash
python manage.py migrate
```

Skopiuj .env-example oraz usuń '-example' z nazwy pliku tak aby powstał '.env'
Włącz dockera i zbuduj projekt będąc na poziomie docker-compose.yml
```bash
docker compose up --build
```
Każdy kolejny raz po zbudowaniu:
```bash
docker compose up
```

Flower:
```bash
http://localhost:5555/
```

Django:
```bash
http://localhost:8000/
```
