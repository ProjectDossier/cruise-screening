## Installation


Create [conda](https://docs.conda.io/en/latest/miniconda.html) environment:

```bash
$ conda create --name dossier python==3.8.8
```

Activate the environment:

```bash
$ source activate dossier
```

Use pip to install requirements:

```bash
(dossier) $ pip install -r requirements.txt
```

### ElasticSearch configuration

Connection parameters to the ElasticSearch database should be stored in `src/dossier_search/utils/example.ini` file containing three params: `cloud_id`, `user`and `password`.

## Running

Make migrations and migrate the database

```bash
(dossier) $ python manage.py makemigrations engine
(dossier) $ python manage.py migrate
```

Finally, run Django server

```bash
(dossier) $ python manage.py runserver 8000
```

Server should be available at http://127.0.0.1:8000/

