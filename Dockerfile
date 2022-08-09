FROM python:3
ADD requirements.txt /
CMD ["source",  "venv/bin/activate"]
RUN pip install -r requirements.txt
COPY src .
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh", "$INST"]