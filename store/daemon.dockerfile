FROM python:3

RUN mkdir -p /opt/src/store/daemon
WORKDIR /opt/src/store

COPY configuration.py ./configuration.py
COPY models.py ./models.py
COPY requirements.txt ./requirements.txt
COPY roleDecorator.py ./roleDecorator.py
COPY daemon/application.py ./daemon/application.py

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src/store/"

ENTRYPOINT ["python", "daemon/application.py"]