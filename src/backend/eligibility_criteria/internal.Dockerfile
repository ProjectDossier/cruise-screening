FROM nvidia/cuda:12.9.0-cudnn-runtime-ubuntu24.04

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

RUN apt-get update -y \
    && apt-get install -y --no-install-recommends python3 python3-pip

COPY requirements.txt requirements_internal.txt requirements_external.txt ./
RUN pip install --break-system-packages torch==2.7.0 --index-url https://download.pytorch.org/whl/cu128 \
    && pip install --break-system-packages -r requirements.txt \
    && pip install --break-system-packages -r requirements_internal.txt

COPY . .
RUN pip install --break-system-packages .[internal]

ENTRYPOINT ["run-api-internal"]