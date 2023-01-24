FROM ubuntu:latest

RUN apt-get update -y

RUN apt install python3-pip -y

RUN apt install ffmpeg -y

RUN apt-get install flac

RUN mkdir /app

WORKDIR /app

ADD . .

RUN pip install -r requirements.txt

CMD bash start
