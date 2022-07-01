FROM golang:1.17-alpine as tools-builder

ENV ARCH=amd64

RUN apk add --no-cache git build-base krb5-dev \
    && git clone https://github.com/mongodb/mongo-tools.git --depth 1 --branch 100.5.3

WORKDIR mongo-tools
RUN GOARCH=$ARCH ./make build

FROM python:3.10-alpine as mongob-builder

RUN pip install --no-cache-dir APScheduler==3.9.1 PyYAML==6.0

FROM python:3.10-alpine

WORKDIR /mongob

COPY --from=tools-builder /go/mongo-tools/bin/* /usr/bin/
COPY --from=mongob-builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY main.py .

VOLUME ["/mongob", "/backup"]

ENV PYTHONUNBUFFERED=0

CMD ["python", "main.py"]