FROM tensorflow/tensorflow:0.12.0
# FROM continuumio/anaconda

MAINTAINER Kelvin Guu <guu.kelvin@gmail.com>

# Add the PostgreSQL PGP key to verify their Debian packages.
# It should be the same key as https://www.postgresql.org/media/keys/ACCC4CF8.asc
RUN apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8

# Add PostgreSQL's repository. It contains the most recent stable release of PostgreSQL, ``9.3``.
RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ precise-pgdg main" > /etc/apt/sources.list.d/pgdg.list

# Install ``python-software-properties``, ``software-properties-common`` and PostgreSQL 9.3
# There are some warnings (in red) that show up during the build. You can hide
# them by prefixing each apt-get statement with DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y python-software-properties software-properties-common postgresql-9.3 postgresql-client-9.3 postgresql-contrib-9.3

RUN apt-get update
RUN apt-get --yes --force-yes install libffi6 libffi-dev libssl-dev libpq-dev git

RUN jupyter nbextension enable --py --sys-prefix widgetsnbextension  # add Jupyter notebook extension

RUN pip install fabric
RUN pip install pyOpenSSL==16.2.0
RUN pip install psycopg2==2.6.1
RUN pip install SQLAlchemy==1.1.0b3
RUN pip install cherrypy==8.1.2
RUN pip install bottle==0.12.10
RUN pip install boto==2.43.0

RUN pip install nltk==3.2.1
RUN python -m nltk.downloader punkt  # download tokenizer data

RUN pip install keras==1.1.0
RUN pip install http://download.pytorch.org/whl/cu75/torch-0.1.11.post5-cp27-none-linux_x86_64.whl
RUN pip install pyhocon line_profiler pytest tqdm faulthandler python-Levenshtein gitpython futures jsonpickle prettytable tensorboard_logger