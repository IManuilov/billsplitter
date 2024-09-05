FROM python:3.12-bullseye

RUN apt-get update && \
    apt-get install -y python3-pip python3-dev


RUN mkdir src
WORKDIR /workspace/src

ADD ./requirements.txt /workspace/src/requirements.txt
RUN pip install -r requirements.txt && pip list

WORKDIR /workspace
COPY . /workspace

CMD ["python", "-m", "bot"]

