# politeiamancer

## minikube up n' running
```sh
minikube start
eval "$(ssh-agent -s)"
```

## Building the Reddit ingester

```sh
cd ./reddit_extract
docker build -t politeiamancer-reddit_extract:0.0.7 .
```

## Working with the helm chart

```sh
helm dependency update ./helm
helm install politeiamancer --namespace politeiamancer --create-namespace ./helm
helm uninstall politeiamancer --namespace politeiamancer
```

## TODO

[ ] Figure out what to do about ready/liveness probes- currently disabled