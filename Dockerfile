# syntax=docker/dockerfile:1

FROM python:3.9-slim
WORKDIR /Pixscale_Telegram
COPY . .
RUN apt-get update && apt-get install -y wget
RUN wget -i url_list.txt -P /pretrained_models

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

CMD [ "python3", "run.py", "--host=0.0.0.0"]