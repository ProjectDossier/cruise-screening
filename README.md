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

Project was tested on Python 3.9+. It will not run on Python 3.8 and below because of type hints for generics.

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

npm install bulma-calendar


### 1.2 Postgres database

[Install PostgreSQL](https://www.postgresql.org/download/)

#### macOS

*Based on this [gist](https://gist.github.com/phortuin/2fe698b6c741fd84357cec84219c6667)*

`brew install postgresql@14`

Run server:

`pg_ctl -D /opt/homebrew/var/postgresql@14 start`

Note: if you’re on Intel, the /opt/homebrew probably is `/usr/local`.

Start psql and open database `postgres`, which is the database postgres uses itself to store roles, permissions, and structure:

```bash
$ psql postgres
```

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

#### Configuration

Next steps common for Ubuntu and macOS.

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
```

Quit psql, because we will log in with the new role (=cruise_literature_user) to create a database:

```postgres
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

Update the DATABASE_URL entry in the `.env` file (see 2.1 Before first run). Replace `SYSTEM_USERNAME` with your system username and `YOUR_PASSWORD` with your desired database password.

```text
DATABASE_URL=postgres://SYSTEM_USERNAME:YOUR_PASSWORD@localhost:5432/cruise_literature
```


### 1.3 ElasticSearch and Search API

Check [backend API](src/backend/README.md) documentation to learn more about installation.

In order to use [CORE search API](https://core.ac.uk/services/api) create a file `data/core_api_key.txt` and insert your API key.
Next, change `SEARCH_WITH_CORE` to  `True` in [`cruise_literature/settings.py`](src/cruise_literature/cruise_literature/settings.py).

### 1.4 Text to text API

It is a separate `flask` application that can be used to generate text predictions (question answering, summarisation) for a given text.
It is not necessary and can be switched off in the [`cruise_literature/settings.py`](src/cruise_literature/cruise_literature/settings.py) by setting:

```python
TEXT_TO_TEXT_API = False
```

Check [prompt_API](src/backend/prompt_api/README.md) documentation to learn more about installation.


## <a name='running' /> 2. Running

### 2.1 Before first run

This fields will also apply after making some changes or updating the code, when the database could be out of sync with the code.

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

Run Django server:

```bash
(cruise-literature)$ python manage.py runserver YOUR_IP:YOUR_PORT
```
