FROM nvidia/cuda:12.9.0-base-ubuntu24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update -y \
    && apt-get install -y --no-install-recommends python3 python3-venv python3-pip

RUN python3 -m venv /app/.venv \
    && . /app/.venv/bin/activate

COPY requirements.txt /app/requirements.txt
RUN /app/.venv/bin/pip install --upgrade --no-cache-dir pip \
    && /app/.venv/bin/pip install torch==2.7.0 --index-url https://download.pytorch.org/whl/cu128 \
    && /app/.venv/bin/pip install -r /app/requirements.txt

COPY . /app
RUN /app/.venv/bin/pip install --no-cache-dir /app

ENTRYPOINT ["/app/.venv/bin/python", "-m", "run-api-external"]