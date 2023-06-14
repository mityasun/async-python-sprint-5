FROM python:3.11

WORKDIR /files-service

COPY ./requirements.txt .

RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

COPY . .

RUN chmod +x scripts/entrypoint.sh
