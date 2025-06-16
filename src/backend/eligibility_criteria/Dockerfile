FROM nvidia/cuda:12.1.1-runtime-ubuntu20.04

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Warsaw
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get update -y
RUN apt-get install -y python3-pip python3.12

COPY requirements.txt /app/requirements.txt
RUN apt-get update && \
    pip install --no-cache-dir -r /app/requirements.txt

COPY . /app
RUN cd /app
RUN pip install --no-cache-dir .

ENTRYPOINT ["run-api"]