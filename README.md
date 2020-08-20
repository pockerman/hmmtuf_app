## Dependencies

- <a href="https://www.djangoproject.com/">django</a>
- <a href="https://docs.celeryproject.org/en/stable/getting-started/introduction.html">celery</a>
- <a href="https://pomegranate.readthedocs.io/en/latest/">pomegranate</a>
- <a href="https://www.sqlite.org/index.html">SQLite</a>

## Setup the project locally

1. ```cd``` to the top-level directory of the project i.e. where the ```manage.py``` file is located
2. Issue: ```python manage.py makemigrations```
3. Issue: ```python manage.py migrate```

The last two commands will setup the needed DB tables. You can now launch the development server

```
python manage.py runserver
```

## Setup ```admin``` site

1. Make sure that you have applied the migrations from ```admin``` and ```auth``` applications
2. Issue: ```python manage.py createsuperuser```
3. Fill in the details asked
4. Fire up the development server and visit ```http://127.0.0.1:8000/admin``` to login

## DB Handling

Currently, the project uses SQLite the default backend 
in Django. The following are some commands we can use during the
development

- Launch the ```dbshell```

```python manage.py dbshell```

- View tables and databases

```.tables```
```.databases```

- Drop all model tables

```python manage.py migrate zero``` 