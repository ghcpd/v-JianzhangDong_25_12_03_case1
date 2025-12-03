# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app

# Install build deps for packages like lxml
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libxml2-dev libxslt1-dev zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN python -m pip install --upgrade pip && \
    python -m pip install -r requirements.txt

COPY app ./app
COPY tests ./tests
COPY run_test.sh ./run_test.sh

RUN chmod +x /app/run_test.sh

CMD ["/app/run_test.sh"]
