FROM python:3.11.2-slim-bullseye

ARG TZ=America/New_York

VOLUME "/config"

RUN \
    pip install requests \
    && pip install python-telegram-bot \
    && pip cache purge

RUN mkdir /app
COPY ./ddnsup.py /app
RUN chmod 755 /app/ddnsup.py

ENTRYPOINT [ "python3", "-u", "/app/ddnsup.py" ]