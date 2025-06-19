# ![cruise-logo.png](src%2Fcruise_literature%2Fstatic%2Fimg%2Fcruise-logo-small.png) CRUISE-screening 

---

### Table of contents
1. [Installation](#installation)
2. [Running](#running)


---

## <a name='installation' /> 1. Installation

This project contains four parts:

- Python Django backend serving the web application
- Postgres database for storing user data
- ElasticSearch database for documents with search API [docker]
- Text2Text API for automatic screening

As a minimum, you need to install the first two parts.

### 1.1 Python Django Backend


Project was tested on Python 3.12. It will not run on Python 3.8 and below because of type hints for generics. You need to install `uv` in order to run the project. 

npm install bulma-calendar


### 1.2 Postgres database


#### Configuration


Start psql and open database:

```bash
$ bash setup.sh
```

Update the DATABASE_URL entry in the `.env` file (see 2.1 Before first run). Replace `SYSTEM_USERNAME` with your system username and `YOUR_PASSWORD` with your desired database password.

```text
DATABASE_URL=postgres://SYSTEM_USERNAME:YOUR_PASSWORD@localhost:5433/cruise_literature
```


### 1.3 ElasticSearch and Search API

Check [backend API](src/backend/search_app/README.md) documentation to learn more about installation.

In order to use [CORE search API](https://core.ac.uk/services/api) create a file `data/core_api_key.txt` and insert your API key.
Next, change `SEARCH_WITH_CORE` to  `True` in [`cruise_literature/settings.py`](src/cruise_literature/cruise_literature/settings.py).

### 1.4 Text to text API

It is a separate `flask` application that can be used to generate text predictions (question answering, summarisation) 
for a given text and classify texts using binary classification.
It is not necessary and can be switched off in the [`cruise_literature/settings.py`](src/cruise_literature/cruise_literature/settings.py) by setting:

```python
ML_API = False
```

Check [prompt_API](src/backend/ml_api/README.md) documentation to learn more about installation.


## <a name='running' /> 2. Running

### 2.1 Before first run

This fields will also apply after making some changes or updating the code, when the database could be out of sync with the code.

In the top level directory of the project, create a `.env` file and fill it with the following fields:

```text
DATABASE_URL=postgres://user:password@host:port/dbname
```

Go into `src/cruise_literature/` directory: 

```bash
(cruise-literature)$ cd src/cruise_literature/
```

Create `.env` file in that directory and fill it with the following fields ([read more](https://django-environ.readthedocs.io/en/latest/quickstart.html)):

```text
DEBUG=True
SECRET_KEY=your-secret-django-key
ALLOWED_HOSTS=
DATABASE_URL=postgres://user:password@host:port/dbname
```

Make migrations and migrate the database

```bash
(cruise-literature)$ python manage.py makemigrations
(cruise-literature)$ python manage.py migrate
```

Create superuser:

```bash
(cruise-literature)$ python manage.py createsuperuser
```

Fill in sample data into the database

```bash
(cruise-literature)$ python manage.py loaddata users_data.json
(cruise-literature)$ python manage.py loaddata search_engines.json
```


### 2.2 On a local host

#### Postgres database

To start the Postgres database, run on macOS:

```bash
$ pg_ctl -D /opt/homebrew/var/postgresql@14 start
```

#### Django server

Finally, run Django server

```bash
(cruise-literature)$ python manage.py runserver 8000
```

Server should be available at http://127.0.0.1:8000/


### 2.3 Deployment on prod server

Add `YOUR_IP` to `ALLOWED_HOSTS` in `.env` file, for example:

```text
ALLOWED_HOSTS=123.456.789.0
```

In the `src/backend/search_app/docker-compose.yml` file modify the IP address in the following line:

```text
network.host=0.0.0.0
```

Run Django server:

```bash
(cruise-literature)$ python manage.py runserver YOUR_IP:YOUR_PORT
```
