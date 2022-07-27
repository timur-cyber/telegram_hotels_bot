FROM python:3
ADD requirements.txt /
RUN pip install -r requirements.txt
COPY src .
CMD [ "python", "./main.py" ]