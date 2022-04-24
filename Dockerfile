FROM python:alpine3.7
RUN apt-get update
RUN apt-get install -y libmagickwand-dev imagemagick
COPY requirements.txt /
RUN pip3 install -r /requirements.txt
COPY . .
CMD ["gunicorn"  , "-b", "0.0.0.0:8888", "main:app"]