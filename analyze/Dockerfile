FROM apache/spark-py:v3.4.0

# For some reason, this is the default username for the Spark image.
ARG spark_user=185

# Set up working dir
WORKDIR /analyze
COPY ./analyze.py ./analyze.py
COPY ./requirements.txt ./requirements.txt

# For some reason, NLTK can only be installed as `root` in the Spark image.
# No matter- I'll just install as root, and swap right back.
USER root
RUN pip install -r requirements.txt

# Install the VADER lexicon, which I need for sentiment analysis
RUN python3 -m nltk.downloader -d /usr/local/share/nltk_data vader_lexicon

USER ${spark_user}

# Let's rock!
CMD sleep 75 && \
    /opt/spark/bin/spark-submit \
        # Stuff with --packages in k8s is jacked in this Spark ver. but allegedly fixed in newer versions 
        # see: https://github.com/apache/spark/pull/38828
        --conf spark.driver.extraJavaOptions="-Divy.cache.dir=/tmp -Divy.home=/tmp" \
        # Can't line-break this blob of stuff else Spark blows up (๑ᵕ⌓ᵕ̤)
        --packages com.datastax.spark:spark-cassandra-connector_2.12:3.5.0,org.apache.spark:spark-streaming-kafka-0-10_2.12:3.5.0,org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 \
        analyze.py
