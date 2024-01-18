from kubernetes import client, config
from prometheus_client import start_http_server, Gauge
import time

# Initialize metrics
DEPLOYMENT_STATUS = Gauge('kubernetes_deployment_status', 'Deployment status', ['namespace', 'deployment'])

def fetch_deployment_statuses():
    config.load_kube_config()  # or load_incluster_config() for in-cluster deployment
    v1 = client.AppsV1Api()
    deployments = v1.list_deployment_for_all_namespaces()
    for dep in deployments.items:
        status = 1 if dep.status.replicas == dep.status.ready_replicas else 0
        DEPLOYMENT_STATUS.labels(dep.metadata.namespace, dep.metadata.name).set(status)

if __name__ == '__main__':
    start_http_server(8000)
    while True:
        fetch_deployment_statuses()
        time.sleep(60)

