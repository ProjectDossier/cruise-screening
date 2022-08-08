## Using the Search Backend REST API

### Starting ElasticSearch and the API

First install [docker](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-20-04) and [docker-compose](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-compose-on-ubuntu-20-04#step-1-installing-docker-compose)

To persist the elasticsearch database, create a folder `[your/directory/on/your/local/]`.
Use `chmod 777 [your/directory/on/your/local/]` to set the correct permissions for elastic search.

Also, select a port number PORT_ES (default `9200`) which is used to connect to elasticsearch and a port number PORT_API (default `9880`) to connect to the search app API.

Create a `docker-compose-local.yml` file containing the following:
```
version: "2"
services:
  search_app:
    ports:
      - "PORT_API:8880"
  es:
    volumes:
      - "[your/directory/on/your/local/]:/usr/share/elasticsearch/data"
    ports:
      - "PORT_ES:9200"
```

The first time, you need to build the images using:

```bash
$ docker-compose -f docker-compose.yml -f docker-compose-local.yml  build
```
By typing `-f docker-compose.yml` and then `-f docker-compose-local.yml` the data from the local file overwrites the default.

Then you can start the services using:
```bash
$ docker-compose -f docker-compose.yml -f docker-compose-local.yml  up
```

ElasticSearch will be accessible on your local machine at `127.0.0.1:PORT_ES`.

### Add docs to the index

Create a `data` folder in the root directory. Add `AMiner_sample.jsonl`,`wikipedia_taxonomy.json`,`wikipedia_taxonomy.xml`, `acm_ccs.xml` files to the `data/` folder. You can find these files on gdrive (link inside Trello)

```bash
$ python scripts/add_docs.py
```

You can parametrise the script by passing other jsonl file with the `--data_path` param.

### Connect to the API

The API accepts the following requests:


```
/search
```
**Method:**  _POST_

**Input:**
```
{
    "query": <your-query>
}
```
**Output:**
```
{
    "results": {
        "hits": {
            "hits": [list-of-es-document-dicts]
        }
    }
}
```
