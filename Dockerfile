FROM centos:7
MAINTAINER  <yfe@protonmail.com>

RUN yum update
RUN yum upgrade

RUN yum install python2-dev python-pip 


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
    # Install conda as jovyan
    RUN cd /tmp && \
        mkdir -p $CONDA_DIR && \
	wget --quiet https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh \
	-O installer.sh && \
	/bin/bash installer.sh -f -b -p $CONDA_DIR && \
	rm installer.sh 

# Install TAlib as unicorn
RUN cd /tmp && \
    wget --quiet https://github.com/mrjbq7/ta-lib/archive/TA_Lib-0.4.10.tar.gz  && \
    tar xvzf  TA_Lib-0.4.10.tar.gz  && \
    cd ta-lib && \
    ./configure --prefix=/usr && \
    make -j 2 && \
    sudo make install

COPY requirements.txt $HOME
RUN cd
RUN conda install --file requirements.txt

USER unicorn


