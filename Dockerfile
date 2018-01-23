FROM ubuntu:16.04 
WORKDIR /var/www/shipit/

# Update OS packages
RUN apt-get update && apt-get -y upgrade

# Install necessary OS packages
RUN apt-get install --no-install-recommends --no-install-suggests -y \
	build-essential \
	python3 \
	python3-dev \
	python3-setuptools \
	python3-pip \
	git

#RUN apt-get install --no-install-recommends --no-install-suggests -y \
#	nginx

# Update pip; install necessary pip packages
RUN pip3 install --upgrade pip
RUN pip3 install wheel uwsgi

# Install application requirements and code
# requirements.txt is copied before the rest for rebuild speed reasons
COPY requirements.txt /var/www/shipit/
RUN pip3 install -r requirements.txt

# Copy files
COPY . /var/www/shipit/
#RUN ln -s /var/www/app/nginx-app.conf /etc/nginx/conf.d/
#RUN /etc/init.d/nginx restart

# Copy the repo containing the ML model
# git clone 

# Do the thing
EXPOSE 5000
ENTRYPOINT uwsgi /var/www/shipit/config/uwsgi-app.ini
