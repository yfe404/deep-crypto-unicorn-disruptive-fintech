FROM centos:7
MAINTAINER  <yfe@protonmail.com>

RUN yum update -y
RUN yum upgrade -y

#RUN yum install -y python2-dev python-pip 
RUN yum install -y wget bzip2 make gcc* python-dev 

# Configure environment
ENV CONDA_DIR /opt/conda
ENV PATH $CONDA_DIR/bin:$PATH
ENV SHELL /bin/bash
ENV NB_USER unicorn
ENV NB_UID 1000
ENV HOME /home/$NB_USER
ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8

# Create unicorn user with UID=1000 and in the 'users' group
RUN useradd -m -s /bin/bash -N -u $NB_UID $NB_USER && \
    mkdir -p $CONDA_DIR && \
        chown $NB_USER $CONDA_DIR


USER unicorn
RUN mkdir /home/unicorn/work 

# Install conda as unicorn
RUN cd /tmp && \
    mkdir -p $CONDA_DIR && \
    # Install conda as unicorn
     cd /tmp && \
        mkdir -p $CONDA_DIR && \
	wget --quiet https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh \
	-O installer.sh && \
	/bin/bash installer.sh -f -b -p $CONDA_DIR && \
	rm installer.sh 


#RUN conda install -y numpy 
USER root

# Install TAlib as root
RUN cd /tmp && \
    wget --quiet https://downloads.sourceforge.net/project/ta-lib/ta-lib/0.4.0/ta-lib-0.4.0-src.tar.gz  && \
    tar xvzf  ta-lib-0.4.0-src.tar.gz  && \
    cd ta-lib && \
    ./configure --prefix=/usr && \
    make && \
    make install
 
COPY requirements.txt $HOME
RUN cd
RUN conda install --file requirements.txt

USER unicorn


