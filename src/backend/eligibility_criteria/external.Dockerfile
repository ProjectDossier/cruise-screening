FROM python:3.12.11-slim-bookworm

WORKDIR /app

COPY requirements.txt requirements_internal.txt requirements_external.txt ./
RUN pip3 install --upgrade --no-cache-dir pip \
    && pip3 install -r requirements.txt \
    && pip3 install -r requirements_external.txt

COPY src ./src
COPY config.yaml pyproject.toml setup.py ./
RUN pip3 install --no-cache-dir .[external]

ENTRYPOINT ["run-api-external"]