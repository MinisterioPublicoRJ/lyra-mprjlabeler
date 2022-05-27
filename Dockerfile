FROM python:3.9

RUN apt-get update \
    && apt-get -y install build-essential \
    && apt-get -y install  libyaml-dev \
    && apt clean

WORKDIR /app

COPY . /app

RUN mkdir -p /media

RUN pip --trusted-host=pypi.python.org --trusted-host=pypi.org --trusted-host=files.pythonhosted.org install -U pip
RUN pip --trusted-host=pypi.python.org --trusted-host=pypi.org --trusted-host=files.pythonhosted.org install -r requirements-dev.txt

RUN python manage.py collectstatic --noinput

VOLUME ["/media"]
