FROM python:3.6
MAINTAINER Bonrg
ENV TZ=Asia/Almaty
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN wget http://dl.google.com/linux/deb/pool/main/g/google-chrome-unstable/google-chrome-unstable_74.0.3729.28-1_amd64.deb
RUN apt update --fix-missing
RUN apt-get install -f -y ./google-chrome-unstable_74.0.3729.28-1_amd64.deb
RUN apt-get install -y libicu-dev

RUN mkdir /src
ADD requirements.txt /src/
WORKDIR /src
RUN pip install -r requirements.txt
ADD /src/ /src/
