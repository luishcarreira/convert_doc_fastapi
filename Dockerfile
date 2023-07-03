# 
FROM python:3.9

# 
WORKDIR /code

# 
COPY ./requirements.txt /code/requirements.txt

RUN apt-get update && apt-get install -y --no-install-recommends \ 
    python3-setuptools \
    python3-pip \
    python3-dev \
    python3-venv \
    git \
    libreoffice

# 
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 
COPY ./app /code/app

# 
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
