FROM nikolaik/python-nodejs:python3.10-nodejs18

RUN apt-get install -y --no-install-recommends ffmpeg \

COPY . /app/
WORKDIR /app/

RUN pip3 install --no-cache-dir --upgrade --requirement requirements.txt

CMD python3 -m Yukki
