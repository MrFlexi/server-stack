# syntax=docker/dockerfile:1
#FROM python:3.7
FROM python:3.7-alpine


COPY . /var/www/
WORKDIR /var/www/

ENV APP_ENV=development

# RUN apt-get install --no-cache gcc musl-dev linux-headers
RUN apk add --no-cache jpeg-dev zlib-dev
RUN apk add --no-cache --virtual .build-deps build-base linux-headers
RUN apk add --no-cache gcc musl-dev linux-headers


RUN pip3 install -r requirements.txt --no-cache-dir

EXPOSE 5000

CMD ["python","app.py"]
