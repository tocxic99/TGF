FROM python:3.12.10

RUN apt update && apt upgrade -y
RUN apt install git -y
COPY requirements.txt /requirements.txt

RUN cd /
RUN pip3 install -U pip && pip3 install -U -r requirements.txt
RUN mkdir /Steve-Forward-Bot
WORKDIR /Steve-Forward-Bot
COPY . /Steve-Forward-Bot
CMD gunicorn app:app & python3 main.py
