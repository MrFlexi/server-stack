# syntax=docker/dockerfile:1
#FROM python:3.7
FROM python:3.9-alpine


COPY . /var/www/
WORKDIR /var/www/

ENV APP_ENV=development

# RUN apt-get install --no-cache gcc musl-dev linux-headers
RUN apk add --no-cache jpeg-dev zlib-dev
RUN apk add --no-cache --virtual .build-deps build-base linux-headers
RUN apk add --no-cache gcc musl-dev linux-headers


RUN pip3 install -r requirements.txt --no-cache-dir

EXPOSE 5000

CMD ["python","-u","app.py"]
#CMD ["uvicorn", "FastApi.fast:app", "--host", "0.0.0.0", "--port", "8000","--reload"]
#CMD ["sh", "./start_python_services.sh"]
