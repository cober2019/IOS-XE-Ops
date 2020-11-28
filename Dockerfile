FROM python:3
WORKDIR /usr/src/app
COPY . .
RUN apt -y update
RUN pip3 install -r requirements.txt
EXPOSE 5001
CMD [“python3”, “./app.py”]
