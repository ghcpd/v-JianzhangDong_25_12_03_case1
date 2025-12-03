FROM python:3.11-slim

# Install build deps and pip
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential gcc libxml2-dev libxslt1-dev libffi-dev libssl-dev \
    && python -m pip install --upgrade pip setuptools wheel

WORKDIR /app

# Copy pinned requirements and install
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy project files
COPY . /app

CMD ["/bin/bash"]
