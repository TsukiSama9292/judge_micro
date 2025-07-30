ARG PYTHON_TAG=3.9-bookworm
FROM python:${PYTHON_TAG}

RUN apt-get update && \
    apt-get install -y \
    make && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir /app
WORKDIR /app

COPY * /app/

RUN make clean && make build