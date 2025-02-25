FROM python:3.13.2-slim-bookworm AS builder

ARG TZ=America/New_York
RUN apt update && DEBIAN_FRONTEND=noninteractive apt -yq install gcc make
RUN pip install requests python-telegram-bot

FROM python:3.13.2-slim-bookworm

ARG TZ=America/New_York
ARG PYVER=3.13

VOLUME "/config"

COPY --from=builder /usr/local/lib/python$PYVER/site-packages/ /usr/local/lib/python$PYVER/site-packages/

RUN mkdir /app
COPY ./ddnsup.py /app
RUN chmod 755 /app/ddnsup.py

ENTRYPOINT [ "python3", "-u", "/app/ddnsup.py" ]
