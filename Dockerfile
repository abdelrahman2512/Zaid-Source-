FROM nikolaik/python-nodejs:python3.9-nodejs18
RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt-get install -y --no-install-recommends ffmpeg
COPY . /app/
WORKDIR /app/
RUN pip3 install --no-cache-dir --upgrade --requirement requirements.txt
CMD python3 -m Yukki
