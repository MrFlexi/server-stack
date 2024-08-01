# syntax=docker/dockerfile:1
#FROM python:3.7
#FROM python:3.9-alpine
#FROM python:3.12.4-alpine
FROM ultralytics/ultralytics:latest-python

#COPY . /var/www/
#WORKDIR /var/www/

COPY . /var/server-stack/
WORKDIR /var/server-stack/

ENV APP_ENV=development

#RUN apt-get install --no-cache gcc musl-dev linux-headers
RUN apt install libjpeg-dev zlib1g-dev

#RUN ap add --no-cache jpeg-dev zlib-dev
#RUN apk add --no-cache --virtual .build-deps build-base linux-headers

RUN pip3 install -r requirements.txt --no-cache-dir

EXPOSE 5000

CMD ["python","-u","./FlaskApp/app.py"]
#CMD ["uvicorn", "FastApi.fast:app", "--host", "0.0.0.0", "--port", "8000","--reload"]
#CMD ["sh", "./start_python_services.sh"]
