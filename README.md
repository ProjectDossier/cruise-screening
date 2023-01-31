# CRUISE-literature 

---

### Table of contents
1. [Installation](#installation)
2. [Running](#running)


---

## <a name='installation' /> 1. Installation

### 1.1 Python Django Backend

Project was tested on Python 3.9+. 

Create [conda](https://docs.conda.io/en/latest/miniconda.html) environment:

```bash
$ conda create --name cruise-literature python==3.9.12
```

Activate the environment:

```bash
$ source activate cruise-literature
```

Use pip to install requirements (you will need `g++` to install fasttext):

```bash
(cruise-literature)$ pip install -r requirements.txt
```

If you have a GPU-enabled device:

```bash
(cruise-literature)$ pip install -r requirements-gpu.txt
```


### 1.2 ElasticSearch and Search API

Checkout [the backend](src/backend/README.md)

In order to use [CORE search API](https://core.ac.uk/services/api) create a file `data/core_api_key.txt` and insert your API key.
Next, change `SEARCH_WITH_CORE` to  `True` in `src/cruise_literature/cruise_literature/settings.py`. 

### 1.3 Postgres database

#### Ubuntu

```bash
$ sudo apt install postgresql postgresql-contrib
```

```bash
$ service postgresql start
```

Start postgres server

```bash
$ sudo systemctl start postgresql.service
```

##### Configuration

Replace `SYSTEM_USERNAME` with your system username and `YOUR_PASSWORD` with your desired database password.

You can check what is your `SYSTEM_USERNAME` with the following command:

```bash
$ whoami
```

Start psql and open database:

```bash
$ sudo -u postgres psql
```

Create new role for cruise application, set its name same as your `SYSTEM_USERNAME`, give `LOGIN` and `CREATEDB` permissions; set `YOUR_PASSWORD` password:

```postgres
postgres-# CREATE ROLE SYSTEM_USERNAME WITH LOGIN;
postgres-# ALTER ROLE SYSTEM_USERNAME CREATEDB;
postgres-# ALTER  USER SYSTEM_USERNAME WITH  PASSWORD 'YOUR_PASSWORD';
postgres-# \q
```

On shell, open psql with `postgres` database with our new user.

```bash
$ psql postgres
```

Note that the postgres prompt looks different, because you’re not logged in as a root user anymore. Create a `cruise_literature` database and grant all privileges to our `SYSTEM_USERNAME` user:

```postgres
postgres-> CREATE DATABASE cruise_literature;
postgres-> GRANT ALL PRIVILEGES ON DATABASE cruise_literature TO SYSTEM_USERNAME;
```

Update the `DATABASES` entry  in [`cruise_literature/settings.py`](src/cruise_literature/cruise_literature/settings.py):

```python
    ...
    "USER": "SYSTEM_USERNAME",
    "PASSWORD": "YOUR_PASSWORD",
    ...
```

#### 1.4 Text to text API

It is a separate `flask` application that can be used to generate text predictions (question answering, summarisation) for a given text.
It is not necessary and can be switched off in the [settings.py](src/cruise_literature/cruise_literature/settings.py):

```python
TEXT_TO_TEXT_API = False
```

Checkout [prompt api](src/backend/prompt_api/README.md) to learn more about installation.


## <a name='running' /> 2. Running

### 2.1 On a local host

Go into `src/cruise_literature/` directory: 

```bash
(cruise-literature)$ cd src/cruise_literature/
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

Make sure that Django Desktop application is running. 

Finally, run Django server

```bash
(cruise-literature)$ python manage.py runserver 8000
```

Server should be available at http://127.0.0.1:8000/


### 2.2 Deployment on prod server

Add `YOUR_IP` to `ALLOWED_HOSTS` in `cruise_literature/settings.py`

```bash
(cruise-literature)$ python manage.py runserver YOUR_IP:YOUR_PORT
```
