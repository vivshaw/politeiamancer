FROM mcr.microsoft.com/devcontainers/python:3.12

# Pull in all the service dependencies
COPY ../analyze/requirements.txt ./analyze_requirements.txt
COPY ../eda/requirements.txt ./eda_requirements.txt
COPY ../ingest/requirements.txt ./ingest_requirements.txt

# Install service dependencies
RUN pip install -r analyze_requirements.txt
RUN pip install -r eda_requirements.txt
RUN pip install -r ingest_requirements.txt

# Install NLTK corpuses
RUN python3 -m nltk.downloader -d /usr/local/share/nltk_data vader_lexicon
RUN python -m nltk.downloader -d /usr/local/share/nltk_data punkt