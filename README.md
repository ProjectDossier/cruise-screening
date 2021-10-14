## Installation

```bash
$ conda create --name dossier python==3.8.8
```

```bash
$ source activate dossier
```

if using pip use:

```bash
pip install -r requirements.txt
```


## Running


```bash
python manage.py makemigrations engine
```

```bash
python manage.py migrate
```

```bash
python manage.py runserver 8000
```

