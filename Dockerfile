FROM python:3.10

# Keep parity with the existing Finzuu service container setup.
RUN apt-get update && \
    apt-get install -y poppler-utils && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -u 1000 ubuntu && \
    mkdir /finzuu

WORKDIR /finzuu

COPY ./requirements.txt /finzuu

RUN pip install --no-cache-dir -r requirements.txt && \
    chown -R ubuntu:ubuntu /finzuu

USER ubuntu

EXPOSE 12041
