# politeiamancer


## building the docker images

```sh
❯ cd ingest
❯ docker build -t vivshaw/politeiamancer-ingest:{INSERT VERSION HERE} .
❯ docker push vivshaw/politeiamancer-ingest:0.0.10
```

## on docker-compose

```sh
❯ docker-compose up
```

## on kubernetes

don't use these instructions, they're 100% busted

## minikube up n' running
```sh
❯ minikube start
❯ eval "$(ssh-agent -s)"
```

## Working with the helm chart

```sh
❯ helm dependency update ./helm
❯ helm install politeiamancer --namespace politeiamancer --create-namespace ./helm
❯ helm uninstall politeiamancer --namespace politeiamancer
```

## TODO

[ ] Figure out what to do about ready/liveness probes- currently disabled