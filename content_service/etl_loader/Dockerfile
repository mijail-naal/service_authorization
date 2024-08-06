FROM python:3.11

WORKDIR /opt/etl_loader
COPY requirements.txt requirements.txt

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . .

CMD ["python3", "load_data.py"]
