FROM python:3.6.9-slim

# Application files
COPY ./clean.py ./
COPY ./pull.py ./
COPY ./requirements.txt ./
COPY ./great_expectations.yml ./
COPY ./expectations.py ./

# Install dependencies
RUN pip install --user -r requirements.txt
