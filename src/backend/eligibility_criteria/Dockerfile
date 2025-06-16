FROM nvidia/cuda:12.1.1-runtime-ubuntu20.04

RUN apt-get update && \
    apt-get install -y python3-pip python3.11

COPY requirements.txt /app/requirements.txt
RUN apt-get update && \
    pip install --no-cache-dir -r /app/requirements.txt

COPY . /app
RUN cd /app
RUN pip install --no-cache-dir .

ENTRYPOINT ["run-api"]