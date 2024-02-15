FROM python:3.11

WORKDIR /opt/workspace

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY api.py ./
COPY worker.py ./
