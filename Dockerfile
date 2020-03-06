FROM python:3.6.6-alpine3.7

ENV REDIS_URL="redis://redis:6379" \
    DJANGO_SETTINGS_MODULE="settings"

ADD ./ /opt/otree

RUN apk -U add --no-cache bash \
                          curl \
                          gcc \
                          musl-dev \
                          postgresql \
                          postgresql-dev \
                          libffi \
                          libffi-dev \
	&& pip install --no-cache-dir -r /opt/otree/requirements_server.txt \
    && mkdir -p /opt/init \
    && chmod +x /opt/otree/entrypoint.sh \
    && chmod +x /opt/otree/worker_entrypoint.sh \
    && apk del curl gcc musl-dev postgresql-dev libffi-dev

WORKDIR /opt/otree
VOLUME /opt/init
EXPOSE 80