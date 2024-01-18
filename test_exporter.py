import pytest
from kubernetes.client import AppsV1Api
from unittest.mock import patch
from k8s_deployment_exporter import fetch_deployment_statuses, DEPLOYMENT_STATUS

class MockDeploymentItem:
    def __init__(self, namespace, name, replicas, ready_replicas):
        self.metadata = MockMetaData(namespace, name)
        self.status = MockDeploymentStatus(replicas, ready_replicas)

class MockMetaData:
    def __init__(self, namespace, name):
        self.namespace = namespace
        self.name = name

class MockDeploymentStatus:
    def __init__(self, replicas, ready_replicas):
        self.replicas = replicas
        self.ready_replicas = ready_replicas

class MockDeploymentResponse:
    def __init__(self, deployments):
        self.items = deployments

# Usage in test function
@patch('kubernetes.config.load_kube_config')
@patch.object(AppsV1Api, 'list_deployment_for_all_namespaces')
def test_fetch_deployment_statuses(mock_list_deployments, mock_load_config):
    # Creating mock deployments
    mock_deployments = [
        MockDeploymentItem('default', 'deployment1', 3, 3),
        MockDeploymentItem('default', 'deployment2', 2, 1),
        # Add more mock deployments as needed
    ]

    # Setting the return value of the mocked method
    mock_list_deployments.return_value = MockDeploymentResponse(mock_deployments)

    fetch_deployment_statuses()

    metrics = DEPLOYMENT_STATUS.labels(namespace='default', deployment='deployment1')._value.get()
    assert metrics == 1, "Deployment1 should be fully up and running"

    metrics = DEPLOYMENT_STATUS.labels(namespace='default', deployment='deployment2')._value.get()
    assert metrics == 0, "Deployment2 should not be fully up and running"
