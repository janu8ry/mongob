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
      - ARCH=amd64  # arm64 or arm64
      - TZ=Asia/Seoul
```