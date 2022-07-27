FROM python:3
ADD requirements.txt /
CMD ["source",  "venv/bin/activate"]
RUN pip install -r requirements.txt
COPY src .
CMD [ "python", "./main.py" ]