FROM nvidia/cuda:12.9.1-cudnn-devel-ubuntu20.04

RUN apt-get update -y
RUN apt-get install -y software-properties-common
RUN add-apt-repository -y ppa:deadsnakes/ppa
RUN apt-get update -y
RUN apt-get install -y python3-pip python3.12
RUN pip install google-genai==1.20.0

COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip
RUN apt-get update -y && \
    pip install --no-cache-dir -r /app/requirements.txt

COPY . /app
RUN cd /app
RUN pip install --no-cache-dir .

ENTRYPOINT ["run-api"]