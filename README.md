# politeiamancer


## building the docker images

```sh
❯ cd ingest
❯ docker build -t vivshaw/politeiamancer-ingest:{INSERT VERSION HERE} .
❯ docker push vivshaw/politeiamancer-ingest:{INSERT VERSION HERE}
```

## on docker-compose

```sh
❯ docker-compose up
```

## on kubernetes

don't use these instructions, they're 100% busted

### minikube up n' running
```sh
❯ minikube start
❯ eval $(minikube -p minikube docker-env)
```

### Working with the helm chart

```sh
❯ helm dependency update ./helm
❯ helm install politeiamancer --namespace politeiamancer --create-namespace ./helm
❯ helm uninstall politeiamancer --namespace politeiamancer
```

## TODO

[ ] Figure out what to do about ready/liveness probes- currently disabled