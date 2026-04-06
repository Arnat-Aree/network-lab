FROM python:3.11-alpine

RUN apk update && \
    apk add --no-cache postgresql-libs && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
    pip install psycopg2 redis && \
    apk del .build-deps

# No entrypoint, handled by compose command
