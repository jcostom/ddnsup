FROM python:3.12.0-slim-bookworm

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