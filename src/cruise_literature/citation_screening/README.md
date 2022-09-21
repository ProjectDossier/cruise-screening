# Citation screening

This is the citation screening project readme.




## Installation

### PostgreSQL

*Based on this [gist](https://gist.github.com/phortuin/2fe698b6c741fd84357cec84219c6667)*

[Install postgresql](https://www.postgresql.org/download/)

#### On Mac:

`brew install postgresql@14`

Run server:

`pg_ctl -D /opt/homebrew/var/postgresql@14 start`

Note: if you’re on Intel, the /opt/homebrew probably is `/usr/local`.

Start psql and open database `postgres`, which is the database postgres uses itself to store roles, permissions, and structure:

```bash
$ psql postgres
```

#### Ubuntu

`service postgresql start`

Run server:

`sudo systemctl start postgresql@14-main`

Start psql and open database:

`sudo -u postgres psql`



### Next steps

Create role for application, give login and `CREATEDB` permissions:

```postgres
postgres-# CREATE ROLE cruise_literature_user WITH LOGIN;
postgres-# ALTER ROLE cruise_literature_user CREATEDB;
```

Quit psql, because we will log in with the new role (=cruise_literature_user) to create a database:

```postgres
postgres-# \q
```

On shell, open psql with `postgres` database with user `cruise_literature_user`:

```bash
$ psql postgres -U cruise_literature_user
```

Note that the postgres prompt looks different, because we’re not logged in as a root user anymore. We’ll create a database and grant all privileges to our user:

```postgres
postgres-> CREATE DATABASE cruise_literature;
postgres-> GRANT ALL PRIVILEGES ON DATABASE cruise_literature TO cruise_literature_user;
```

Run migrations and start server:

```bash
$ python manage.py makemigrations
$ python manage.py migrate --database=literature_review
$ python manage.py migrate
$ python manage.py runserver
```


sudo systemctl start postgresql
sudo systemctl enable postgresql




### GROBID

#### server

```bash
docker pull lfoppiano/grobid:0.7.1
docker run -t --rm -p 8070:8070 lfoppiano/grobid:0.7.1
```


#### Client 

Just install 

`pip install grobid_tei_xml`