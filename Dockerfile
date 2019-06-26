FROM amazonlinux:2.0.20190508

ENV PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
    LD_LIBRARY_PATH=/lib64:/usr/lib64:/var/runtime:/var/runtime/lib:/var/task:/var/task/lib \
    PYTHONPATH=/var/runtime

RUN yum -y groupinstall 'Development tools' && yum -y install openssl-devel sqlite-devel wget libffi-devel

RUN cd /usr/local/src && wget https://www.python.org/ftp/python/3.7.3/Python-3.7.3.tgz && \
    tar zxvf Python-3.7.3.tgz && cd Python-3.7.3 && ./configure --prefix=/usr && make && make install
RUN pip3.7 install --upgrade pip && pip3.7 install pipenv

WORKDIR /app
VOLUME /app/vendor

COPY ./Pipfile /app/Pipfile
COPY ./Pipfile.lock /app/Pipfile.lock
RUN pipenv lock -r > requirements.txt