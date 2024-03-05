# politeiamancer

politeiamancer performs sentiment analysis on live streaming comment data from [the /r/politics subreddit](https://www.reddit.com/r/politics/). It tracks overall sentiment, as well as sentiment for comments mentioning the 2024 Presidential candidates specifically.

## Why would I want this?

You too can eat straight from the trash can of ideology, now in realtime! Fun!!

## Why the silly name?

 - [πολιτεία](https://en.wikipedia.org/wiki/Politeia) (Gr.): citizenship, the community of citizens, a polity
 - [μᾰντείᾱ](https://en.wiktionary.org/wiki/%CE%BC%CE%B1%CE%BD%CF%84%CE%B5%CE%AF%CE%B1#Ancient_Greek) (Gr.): prophecy, divination, oracle
 - anything is a perfectly cromulent prefix if you believe hard enough

## Data Protection & Compliance

politeiamancer complies with Reddit's [Developer Data Protection Addendum](https://www.redditinc.com/policies/developer-dpa) by simply not storing any comments. The comments are ingested into Kafka, streamed into Spark for analysis, and then dropped. All that is retained are the analytics results.

## Development

### building the docker images

```sh
❯ cd ingest
❯ docker build -t vivshaw/politeiamancer-analyze:{INSERT VERSION HERE} ./analyze
❯ docker build -t vivshaw/politeiamancer-ingest:{INSERT VERSION HERE} ./ingest
❯ docker build -t vivshaw/politeiamancer-viz:{INSERT VERSION HERE} ./viz
❯ docker push vivshaw/politeiamancer-analyze:{INSERT VERSION HERE}
❯ docker push vivshaw/politeiamancer-ingest:{INSERT VERSION HERE}
❯ docker push vivshaw/politeiamancer-viz:{INSERT VERSION HERE}
```

### on docker-compose

```sh
❯ docker-compose up
```

### on kubernetes

don't use these instructions, they're 100% busted

#### minikube up n' running
```sh
❯ minikube start
❯ eval $(minikube -p minikube docker-env)
```

#### Working with the helm chart

```sh
❯ helm dependency update ./helm
❯ helm install politeiamancer --namespace politeiamancer --create-namespace ./helm
❯ helm uninstall politeiamancer --namespace politeiamancer
```

## TODO

- [ ] Figure out what to do about ready/liveness probes- currently disabled
