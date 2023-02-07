FROM python:3

RUN mkdir -p /opt/src/authentication
WORKDIR /opt/src/authentication

COPY migrate.py ./migrate.py
COPY configuration.py ./configuration.py
COPY models.py ./models.py
COPY requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENV DATABASE_URL authenticationDB

ENTRYPOINT ["python", "./migrate.py"]