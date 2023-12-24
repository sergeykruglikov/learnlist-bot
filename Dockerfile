FROM ubuntu:latest

RUN apt update --quiet && apt install -y python3 python3-pip

RUN mkdir -p /src
COPY src/ /src/
RUN chmod +x /src/learnlist.py
WORKDIR /src

RUN pip3 install --upgrade -r /src/requirements.txt

CMD ["/bin/bash", "-c", "/src/learnlist.py"]

