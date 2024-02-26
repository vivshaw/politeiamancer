FROM apache/spark-py:v3.4.0

# For some reason, this is the default username for the Spark image.
ARG spark_user=185

# Set up working dir
WORKDIR /analyze
COPY ./analyze.py ./analyze.py
COPY ./requirements.txt ./requirements.txt

# For some reason, NLTK can only be installed as `root` in the Spark image.
# No matter- i'll just install as root, and swap right back.
USER root
RUN pip install -r requirements.txt
USER ${spark_user}

# Install the VADER lexicon, which I need for sentiment analysis
RUN python3 -m nltk.downloader -d /analyze/nltk_data vader_lexicon

# Let's rock!
CMD ["python3", "analyze.py"]