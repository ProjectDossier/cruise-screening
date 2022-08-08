## 1. Installation

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

Use pip to install requirements:

```bash
(cruise-literature)$ pip install -r requirements.txt
```

If you have a GPU-enabled device:

```bash
(cruise-literature)$ pip install -r requirements-gpu.txt
```


### 1.2 ElasticSearch and Search API

Checkout [the backend](src/backend/README.md)


## 2. Running

### 2.1 On a local host

Go into `src/cruise_literature/` directory: 

```bash
(cruise-literature)$ cd src/cruise_literature/
```

Make migrations and migrate the database

```bash
(cruise-literature)$ python manage.py makemigrations home document_search concept_search users
(cruise-literature)$ python manage.py migrate
```

Create superuser:

```bash
(cruise-literature)$ python manage.py createsuperuser
```

Fill in sample data into the database

```bash
(cruise-literature)$ python manage.py loaddata users_data.json
```

Make sure that Django Desktop application is running. 

Finally, run Django server

```bash
(cruise-literature)$ python manage.py runserver 8000
```

Server should be available at http://127.0.0.1:8000/


### 2.2 Deployment on prod server

```bash
(cruise-literature)$ python manage.py runserver YOUR_IP:YOUR_PORT
```

## 3. Get Latest Version

### 3.1 Update Your Local Code Version

Before you start work, make sure you have the latest changes.
Go into `src/cruise_literature/` directory: 

	> git pull origin main

## 4. Troubleshooting

### 4.1 M1 Macbook

If you are using a laptop with the M1 chip please change the following line in the [settings.py](src/cruise_literature/cruise_literature/settings.py) file:

```python
M1_CHIP = True
```
see [#130](https://github.com/ProjectDossier/cruise-literature/issues/130) for more details
