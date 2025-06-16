FROM nvidia/cuda:12.1.1-runtime-ubuntu20.04

RUN add-apt-repository -y ppa:deadsnakes/ppa
RUN apt-get update -y
RUN apt-get install -y python3-pip python3.12

COPY requirements.txt /app/requirements.txt
RUN apt-get update && \
    pip install --no-cache-dir -r /app/requirements.txt

COPY . /app
RUN cd /app
RUN pip install --no-cache-dir .

ENTRYPOINT ["run-api"]