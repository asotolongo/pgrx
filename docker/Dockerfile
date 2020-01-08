FROM python:2


COPY . /app
WORKDIR /app
RUN pip install psycopg2
RUN pip install markdown

CMD python ./pgrx.py


