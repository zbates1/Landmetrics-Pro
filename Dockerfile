# syntax=docker/dockerfile:1

FROM python:3.9.19

WORKDIR /code

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .

# Doesn't actually setup a port, so you have to use -p tag in docker run
EXPOSE 5000

# This is for the old repo version, and also 
# for a production ready command.You may need to change the app:app part, or this may be irrelevant when using heroku.
# ENTRYPOINT ["gunicorn", "-c", "gunicorn_config.py", "app:app"]

# I think that this is the right way to do it development
ENTRYPOINT ["python", "main.py"]

