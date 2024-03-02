FROM grafana/grafana:10.2.4

# Grafana doesn't have native Cassandra connectivity, needs plugin
# see: https://grafana.com/grafana/plugins/hadesarchitect-cassandra-datasource/
RUN grafana-cli plugins install hadesarchitect-cassandra-datasource

COPY conf/cassandra.yaml /etc/grafana/provisioning/datasources/cassandra.yaml
COPY conf/dashboard.yaml /etc/grafana/provisioning/dashboards/dashboard.yaml
COPY dashboards /var/lib/grafana/dashboards