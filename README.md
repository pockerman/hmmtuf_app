## Dependencies

- <a href="https://www.djangoproject.com/">django</a>
- <a href="https://docs.celeryproject.org/en/stable/getting-started/introduction.html">celery</a>
- <a href="https://pomegranate.readthedocs.io/en/latest/">pomegranate</a>
- <a href="https://www.sqlite.org/index.html">SQLite</a>

#### Note

You also need to install one of the backends supported by Celery. For more
information see <a href="https://docs.celeryproject.org/en/stable/getting-started/introduction.html#installation">here</a>.



## Setup the project locally

1. ```cd``` to the top-level directory of the project i.e. where the ```manage.py``` file is located
2. Issue: ```python manage.py makemigrations```
3. Issue: ```python manage.py migrate```

The last two commands will setup the needed DB tables. You can now launch the development server.

Alternatively, you can apply migrations only for a specific application:

2. ```python manage.py makemigrations app_name```
3. ```python manage.py migrate app_name```

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

## Monitoring Celery

You can use <a href="https://flower.readthedocs.io/en/latest/">flower</a> in order to monitor Celery

## Deploy

There are several tools that can be used for deployment. A common scenario is using 
<a href="https://gunicorn.org/">Gunicorn</a> a Python WSGI HTTP Server for UNIX and 
<a href="https://nginx.org/en/">nginx</a> an HTTP and reverse proxy server. 

You can find instructions how to deploy the application using Gunicorn and 
nginx <a href="https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-18-04">here</a>.

