import time
from typing import List

from kubernetes import client, config

config.load_kube_config('/home/ubuntu/.kube/config')
k8s_client = client.CoreV1Api()


def get_ready_nodes_count() -> int:
    ready_count = 0
    nodes = k8s_client.list_node().items
    for node in nodes:
        conditions: List = node.status.conditions
        for condition in conditions:
            if condition.type == 'Ready' and condition.status == 'True':
                    ready_count = ready_count + 1
    return ready_count


required_ready_nodes = 2


def wait_for_all_nodes_ready() -> None:
    while True:
        ready_nodes_count = get_ready_nodes_count()
        if ready_nodes_count >= required_ready_nodes:
            print("All nodes ready")
            break
        else:
            print(
                f"Awaiting for {required_ready_nodes} ready nodes. Current number of ready nodes: {ready_nodes_count}")
            time.sleep(10)


if __name__ == '__main__':
    wait_for_all_nodes_ready()
