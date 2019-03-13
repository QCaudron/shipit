FROM ubuntu:16.04 
WORKDIR /var/www/shipit/



# Update OS packages
RUN apt-get update && apt-get -y upgrade



# Install packages needed for Miniconda
RUN apt-get install -y \
	bzip2 \
	build-essential \
	curl \ 
	git \
	libboost-python-dev \
	libpython3-dev \
	python3-dev \
	python3-pip \
	wget

# Download anaconda install
#RUN curl -O https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh

# Turn executable attribute
#RUN chmod +x Miniconda3-latest-Linux-x86_64.sh 

# Install Anaconda
#RUN bash Miniconda3-latest-Linux-x86_64.sh -b

# Remove Instalation file
#RUN rm Miniconda3-latest-Linux-x86_64.sh

# Add Anaconda to the Path
#ENV PATH /root/miniconda3/bin:$PATH 



# Copy local code
COPY . /var/www/shipit/



# Install pipreqs
RUN pip3 install pipreqs 

# Generate a requirements.txt file
RUN pipreqs /var/www/shipit/ --force
RUN /bin/bash -c 'cat /var/www/shipit/requirements.txt'

# Install user packages, from conda where possible and otherwise from pip
#RUN /bin/bash -c 'while read requirement; do conda install -y $requirement || pip install $requirement; done < requirements.txt'
RUN pip3 install -r /var/www/shipit/requirements.txt


# Install uwsgi
RUN pip3 install uwsgi



# Do the thing
EXPOSE 5000
ENTRYPOINT uwsgi /var/www/shipit/config/uwsgi-app.ini

#CMD ["bash"]
