## 1. Installation

### 1.1 Python Backend

Create [conda](https://docs.conda.io/en/latest/miniconda.html) environment:

```bash
$ conda create --name cruise-literature python==3.8.12
```

Activate the environment:

```bash
$ source activate cruise-literature
```

Use pip to install requirements:

```bash
(cruise-literature)$ pip install -r requirements.txt
```

### 1.2 ElasticSearch configuration

First install [docker](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-20-04) and [docker-compose](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-compose-on-ubuntu-20-04#step-1-installing-docker-compose):

Go to the `db` directory. Choose an existing directory on your local instead of [your/directory/on/your/local/] in docker-compose.yml:

- "${HOME}[your/directory/on/your/local/]:/usr/share/elasticsearch/data"

Run docker compose:


```bash
$ cd db
$ docker compose up -d
```

ElasticSearch will start on `9200`

### 1.3 Add docs to the index

Create a `data` folder in the root directory. Add `AMiner_sample.jsonl` file to the `data/` folder.

```bash
python scripts/add_docs.py
```


#### Access ElasticSearch from your local machine

You need to create an SSH tunnel:

```bash
$ ssh -L 9205:127.0.0.1:9200 YOUR_USER@YOUR_IP
```

ElasticSearch will be accessible on your local machine at `127.0.0.1:9005`.

_____
__DEPRECATED:__ Connection parameters to the ElasticSearch database should be stored in `src/dossier_search/utils/example.ini` file containing three params: `cloud_id`, `user`and `password`.
_____


## 2. Running

### 2.1 On a local host

Go into `src/dossier_search/` directory: 

```bash
(cruise-literature)$ cd src/dossier_search/
```

Make migrations and migrate the database

```bash
(cruise-literature)$ python manage.py makemigrations engine
(cruise-literature)$ python manage.py migrate
```

Finally, run Django server

```bash
(cruise-literature)$ python manage.py runserver 8000
```

Server should be available at http://127.0.0.1:8000/


### 2.2 Deployment on prod server

```bash
(cruise-literature)$ python manage.py runserver YOUR_IP:YOUR_PORT
```

