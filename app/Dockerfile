FROM python:3.6.9-slim

# Application files
COPY ./run.sh ./
COPY ./clean.py ./
COPY ./pull.py ./
COPY ./requirements.txt ./
COPY ./great_expectations/ ./great_expectations/

# Install dependencies
RUN pip install -r requirements.txt

# For testing. Will be overidden by ECS container defintion commadnd
CMD ["bash", "run.sh"]
#CMD ["which", "great_expectations"]
