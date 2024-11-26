#!/bin/bash

# Exit script on error
set -e

# Constants
PROJECT_DIR="cruise_literature"
CONDA_ENV="cruise-literature"
PYTHON_VERSION="3.9.12"
POSTGRES_PASSWORD="YOUR_PASSWORD"
POSTGRES_USER=$(whoami)
SECRET_KEY="your-secret-django-key"
MINICONDA_DIR="$HOME/miniconda"

echo "Starting CRUISE-screening setup on Ubuntu..."

# 1. Install required packages
echo "Installing required packages..."
sudo apt update
sudo apt install -y wget curl git g++ postgresql postgresql-contrib python3-pip

# 2. Install Miniconda
if [ -d "$MINICONDA_DIR" ]; then
    echo "Miniconda is already installed at $MINICONDA_DIR."
else
    echo "Installing Miniconda..."
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
    bash miniconda.sh -b -p $MINICONDA_DIR
fi

# Ensure Miniconda is in PATH
export PATH="$MINICONDA_DIR/bin:$PATH"

# Initialize Conda for bash
if ! grep -q "conda initialize" ~/.bashrc; then
    conda init bash
    source ~/.bashrc
fi

# 3. Create Conda environment
if conda info --envs | grep -q "$CONDA_ENV"; then
    echo "Conda environment $CONDA_ENV already exists."
else
    echo "Creating Conda environment..."
    conda create --name $CONDA_ENV python=$PYTHON_VERSION -y
fi
source activate $CONDA_ENV

# 4. Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# 5. Install PostgreSQL and configure
echo "Setting up PostgreSQL..."

# Ensure PostgreSQL service is running
sudo systemctl start postgresql.service

# Switch to a temporary directory to avoid permission issues
CURRENT_DIR=$(pwd)
cd /tmp

# Check if the role exists; create it if necessary
sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname = '$POSTGRES_USER'" | grep -q 1 || sudo -u postgres psql -c "CREATE ROLE $POSTGRES_USER WITH LOGIN PASSWORD '$POSTGRES_PASSWORD';"
sudo -u postgres psql -c "ALTER ROLE $POSTGRES_USER CREATEDB;"

# Check if the database exists; create it if necessary
sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname = '$PROJECT_DIR'" | grep -q 1 || sudo -u postgres psql -c "CREATE DATABASE $PROJECT_DIR OWNER $POSTGRES_USER;"

# Return to the original directory
cd "$CURRENT_DIR"

echo "PostgreSQL setup complete."

# 6. Create and populate .env file
echo "Creating .env file..."
ENV_FILE="src/$PROJECT_DIR/.env"
if [ ! -f "$ENV_FILE" ]; then
    cat <<EOF >"$ENV_FILE"
DEBUG=True
SECRET_KEY=$SECRET_KEY
ALLOWED_HOSTS=
DATABASE_URL=postgres://$POSTGRES_USER:$POSTGRES_PASSWORD@localhost:5432/$PROJECT_DIR
STATIC_ROOT=src/cruise_literature/allstatic
EOF
else
    echo ".env file already exists, skipping creation."
fi

# 7 statics

STATIC_ROOT_DIR="src/cruise_literature/allstatic"
if [ -d $STATIC_ROOT_DIR ]; then
    echo "static root folder already exists, skipping"
else
    mkdir $STATIC_ROOT_DIR
fi

# 8. ElasticSearch and Search API

echo "Checking Docker permissions..."

if ! groups $USER | grep -q "\bdocker\b"; then
    echo "Adding $USER to the docker group..."
    sudo usermod -aG docker $USER
    echo "You need to log out and log back in for changes to take effect, or run 'newgrp docker'."
    exit 1
fi

echo "Docker permissions verified."


echo "Setting up ElasticSearch and API..."

# Step 1: Install Docker and Docker Compose
if ! [ -x "$(command -v docker)" ]; then
    echo "Docker not found. Installing Docker..."
    sudo apt update
    sudo apt install -y docker.io
    sudo systemctl start docker
    sudo systemctl enable docker
fi

if ! [ -x "$(command -v docker-compose)" ]; then
    echo "Docker Compose not found. Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Step 2: Set up ElasticSearch data directory
ES_DATA_DIR="$CURRENT_DIR/es_data"
if [ ! -d "$ES_DATA_DIR" ]; then
    mkdir -p "$ES_DATA_DIR"
    chmod 777 "$ES_DATA_DIR"
fi

# Step 3: Create docker-compose-local.yml
cd "$CURRENT_DIR/src/backend"
DOCKER_COMPOSE_FILE="docker-compose-local.yml"
cat > $DOCKER_COMPOSE_FILE <<EOL
version: "2"
services:
  search_app:
    image: cruise/search_app:latest
    ports:
      - "9880:8880"
  es:
    image: elasticsearch:7.17.10
    environment:
      - discovery.type=single-node
    volumes:
      - "$ES_DATA_DIR:/usr/share/elasticsearch/data"
    ports:
      - "9200:9200"
EOL

# Step 4: Build and start the services
echo "Building and starting ElasticSearch and API containers..."
sudo docker-compose -f docker-compose.yml -f $DOCKER_COMPOSE_FILE build
sudo docker-compose -f docker-compose.yml -f $DOCKER_COMPOSE_FILE up -d

# Step 5: Index documents into ElasticSearch
echo "Indexing documents into ElasticSearch..."
DATA_DIR="es_data"
if [ ! -d "$DATA_DIR" ]; then
    mkdir -p "$DATA_DIR"
    echo "Add the required data files to the $DATA_DIR folder before indexing."
fi

if [ -f "scripts/add_docs.py" ]; then
    python scripts/add_docs.py
else
    echo "Document indexing script not found (scripts/add_docs.py). Skipping indexing."
fi

echo "ElasticSearch setup complete."


# 9. Apply Django migrations and setup
cd "$CURRENT_DIR"
touch "data/core_api_key.txt"
echo "Applying migrations and creating superuser..."
cd src/$PROJECT_DIR

python manage.py makemigrations
python manage.py migrate

if python manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.filter(is_superuser=True).exists())" | grep -q "False"; then
    echo "Creating Django superuser. Follow the prompts..."
    python manage.py createsuperuser
else
    echo "Superuser already exists, skipping creation."
fi

echo "Loading sample data..."
python manage.py loaddata users_data.json || echo "users_data.json already loaded."
python manage.py loaddata search_engines.json || echo "search_engines.json already loaded."

# 8. Run the server
echo "Starting Django development server..."
python manage.py runserver 8000

echo "Setup complete. Visit http://127.0.0.1:8000/ to access the application."