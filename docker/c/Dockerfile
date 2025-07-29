ARG GCC_TAG=15-bookworm
FROM gcc:${GCC_TAG}

RUN apt-get update && \
    apt-get install -y libcjson-dev make && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir /app
WORKDIR /app

COPY * /app/

# Recompile harness to ensure compatibility with container's GLIBC version
RUN make clean && make build