FROM python:3
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY ./requirements.txt /app

RUN apt-get -y install libmariadb-dev

RUN pip install -r requirements.txt && \
    rm requirements.txt

COPY ./manage.py /app
COPY ./app_manager /app/app_manager
COPY ./drink_consumption /app/drink_consumption

COPY ./entrypoint.sh /app/entrypoint.sh
RUN chmod a+x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
