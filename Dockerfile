FROM ubuntu:18.04

RUN apt-get update && apt-get install -y software-properties-common dpkg-dev devscripts equivs
RUN add-apt-repository ppa:jyrki-pulliainen/dh-virtualenv
RUN apt-get update && apt-get install -y dh-virtualenv

WORKDIR /source
ADD package/debian debian
RUN mk-build-deps --install debian/control

ARG POETRY_VERSION=1.1.4
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py \
    | python3 - --version $POETRY_VERSION
ENV PATH="${PATH}:/root/.poetry/bin"

ADD . .

RUN poetry export --output requirements.txt
RUN cp package/setup.py .
RUN dpkg-buildpackage --unsigned-source --unsigned-changes --build=binary
