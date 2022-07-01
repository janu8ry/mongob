# Mongob
Mongob is a MongoDB backup tool built with python,  
inspired by [stefanprodan/mgob](https://github.com/stefanprodan/mgob).

## Features
- scheduled backups
- supports MongoDB 4.0 ~ 5.0
- supports amd64, arm64 architecture
- light image

## Install
Mongob is available on Docker Hub at [janu8ry/mongob](https://hub.docker.com/r/janu8ry/mongob/).   

Supported tags:
- `janu8ry/mongob:latest`, `janu8ry/mongob:amd64` latest build for amd64 architectures
- `janu8ry/mongob:arm64` latest build for arm64 architectures

using docker compose is recommended.   

_docker-compose.yml_
```yml
# docker-compose.yml

version: "3.9"

services:
  mongo:
    image: mongo:latest
    restart: always
    container_name: "mongo"
    ports:
      - "27017:27017"
    volumes:
      -  /data/db:/data/db
    environment:
      - TZ=Asia/Seoul"
  mongob:
    image: janu8ry/mongob:latest
    restart: always
    container_name: "mongob"
    volumes:
      - ./config.yml:/mongob/config.yml
      - ./backup:/backup
    environment:
      - TZ=Asia/Seoul
```

## Configuration
Define your backup plan in `/mongob/config.yml`.  
The config file should follow the form below.  
Backup files are stored in `/backup`.   
   
cron expression is available for `hour`, `minute` config.   
If you're not using authentication, keep `username`, `password` to `null`.

_example config.yml_
```yaml
target:
  host: "mongo"
  port: 27017
  database: "mydb"
  username: "admin"  # or null
  password: "password"  # or null
scheduler:
  hour: "0, 12"  # backup at 0 am, 12pm everyday
  minute: "0"
```

## Logs
View Mongob logs with `docker logs mongob -f`.

## Restore
```shell
docker exec -it mongob /bin/sh
mongorestore --gzip --archive=/backup/xxxx.gz --host mongo:27017 --drop
```

## Build 
- amd64 build
You need amd64 machine to build amd64 image.

```shell
docker build -t mongob:latest --build-arg ARCH=amd64 .
docker image tag mongob:latest mongob:amd64
```

- arm64 build
You need arm64 machine to build arm64 image.

```shell
docker build -t mongob:arm64 --build-arg ARCH=arm64 .
```