FROM python:3.7
ENV PYTHONUNBUFFERED 1

WORKDIR /shipit/

# Install OS Packages
RUN apt-get update && apt-get install -y \
    python-dev \
    python-pip \
    python-setuptools \
    openssl \
    python3-service-identity \
    python3-openssl

# Install pipreqs
RUN pip3 install uwsgi flask pyyaml

# Install user packages, from conda where possible and otherwise from pip
COPY requirements.txt /shipit/
RUN pip3 install -r /shipit/requirements.txt

# Copy local code
COPY . /shipit/

# Do the thing
EXPOSE 5000 5000
CMD ["uwsgi", "--ini", "/shipit/config/uwsgi-app.ini"]
