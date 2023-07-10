FROM python:3.9
 
WORKDIR /app
 
COPY requirements.txt .

RUN apt-get update && apt-get install -y --no-install-recommends \ 
    python3-setuptools \
    python3-pip \
    python3-dev \
    python3-venv \
    git \
    libreoffice
 
RUN pip install --no-cache-dir --upgrade -r requirements.txt
 
COPY . .
