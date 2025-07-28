ARG GCC_TAG=15-bookworm
FROM gcc:${GCC_TAG}

RUN apt-get update && \
    apt-get install -y libcjson-dev make && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir /app
WORKDIR /app

COPY * /app/

# 重新編譯 harness 以確保與容器內 GLIBC 版本兼容
RUN make clean && make build