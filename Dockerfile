FROM python:3.5
MAINTAINER Gabor Ratky <rgabo@rgabostyle.com>

# Spark dependencies
ENV APACHE_SPARK_VERSION 2.0.0
RUN apt-get -y update && \
    apt-get install -y --no-install-recommends openjdk-7-jre-headless && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
ENV HADOOP_VERSION 2.7
RUN cd /tmp && \
        wget -q http://d3kbcqa49mib13.cloudfront.net/spark-${APACHE_SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz && \
        echo "3d46e990c06a362efc23683cf0ec15e1943c28e023e5b5d4e867c78591c937ad *spark-${APACHE_SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz" | sha256sum -c - && \
        tar xzf spark-${APACHE_SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz -C /usr/local && \
        rm spark-${APACHE_SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz
RUN cd /usr/local && ln -s spark-${APACHE_SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} spark

ENV SPARK_HOME /usr/local/spark
ENV PATH $PATH:$SPARK_HOME/bin
ENV PYTHONPATH $SPARK_HOME/python:$SPARK_HOME/python/lib/py4j-0.10.1-src.zip
ENV SPARK_OPTS --driver-java-options=-Xms1024M --driver-java-options=-Xmx4096M --driver-java-options=-Dlog4j.logLevel=info

RUN mkdir -p /awsh
WORKDIR /awsh

COPY requirements.txt /awsh/requirements.txt
RUN pip install -r requirements.txt

COPY requirements-test.txt /awsh/requirements-test.txt
RUN pip install -r requirements-test.txt

COPY . /awsh
RUN pip install .

ENTRYPOINT awsh
