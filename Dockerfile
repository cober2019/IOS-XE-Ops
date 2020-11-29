FROM ubuntu:latest
COPY . /RoutingGUI
WORKDIR /RoutingGUI
RUN apt update
RUN DEBIAN_FRONTEND='noninteractive' apt  install -y python3 python3-dev python3-pip nginx
RUN DEBIAN_FRONTEND='noninteractive' pip3 install uwsgi
RUN DEBIAN_FRONTEND='noninteractive' pip3 install -r requirements.txt
EXPOSE 5000
ENTRYPOINT [ "python3" ]
CMD [ "run.py" ]
