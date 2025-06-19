#!/bin/bash 
# docker
COMPOSE_FILES=(
    ./src/backend/search_app/docker-compose.yml
    ./src/backend/search_app/docker-compose-juno.yml
    ./src/cruise_literature/docker-compose.yaml
)

COMPOSE_ARGS=""
for FILE in "${COMPOSE_FILES[@]}"; do
    COMPOSE_ARGS="$COMPOSE_ARGS -f $FILE"
done

docker-compose $COMPOSE_ARGS up --wait

# uvicorn
CURRENT_DIR=$(pwd)
cd src/backend/ml_api
uv run -m uvicorn app:app &
cd $CURRENT_DIR

# django
cd src/cruise_literature
uv run manage.py makemigrations
uv run manage.py migrate
uv run manage.py loaddata users_data.json
uv run manage.py loaddata search_engines.json
uv run manage.py runserver 8080
cd $CURRENT_DIR
