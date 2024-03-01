FROM grafana/grafana:10.2.4

# Grafana doesn't have native Cassandra connectivity, needs plugin
# see: https://grafana.com/grafana/plugins/hadesarchitect-cassandra-datasource/
RUN grafana-cli plugins install hadesarchitect-cassandra-datasource