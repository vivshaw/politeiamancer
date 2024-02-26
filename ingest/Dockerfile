From python:3.10

# Set up working dir
WORKDIR /ingest
COPY ./ingest.py ./ingest.py
COPY ./requirements.txt ./requirements.txt

# Install Python dependencies
RUN pip install -r requirements.txt

# Let's rock!
CMD ["python3", "ingest.py"]