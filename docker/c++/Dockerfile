ARG GCC_TAG=15-bookworm
FROM gcc:${GCC_TAG}

RUN apt-get update && \
    apt-get install -y \
        g++ nlohmann-json3-dev make && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir /app
WORKDIR /app

COPY * /app/

# 重新編譯 harness 以確保與容器內環境兼容
RUN make clean && make build