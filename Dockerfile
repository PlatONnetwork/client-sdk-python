FROM python:3.6

# Set up code directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# Install Linux dependencies
RUN apt-get update && apt-get install -y libssl-dev

COPY client_sdk_python ./client_sdk_python/
COPY tests ./tests/
COPY ens ./ens/

COPY setup.py .
COPY README.md .

RUN pip install -e .[dev]

WORKDIR /code
