FROM python:3.11

RUN mkdir /inventoryx_api

WORKDIR /inventoryx_api

COPY . /inventoryx_api/

RUN pip install -r requirements.txt