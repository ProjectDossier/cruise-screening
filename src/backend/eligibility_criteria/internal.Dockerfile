FROM nvidia/cuda:12.9.0-base-ubuntu24.04

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

RUN apt-get update -y \
    && apt-get install -y --no-install-recommends python3 python3-venv python3-pip

RUN python3 -m venv .venv

COPY requirements.txt requirements_internal.txt requirements_external.txt ./
RUN . .venv/bin/activate \
    && pip install --upgrade --no-cache-dir pip \
    && pip install torch==2.7.0 --index-url https://download.pytorch.org/whl/cu128 \
    && pip install -r /app/requirements_internal.txt

COPY . .
RUN . .venv/bin/activate \
    && pip install --no-cache-dir .[internal]

ENTRYPOINT ["/app/.venv/bin/python", "-m", "ecriteria_internal.app.py"]