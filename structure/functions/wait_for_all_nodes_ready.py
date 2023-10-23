import time
from kubernetes import client, config

config.load_kube_config()

kube_client = client.CoreV1Api()

def wait_for_node_ready(node_name, timeout_seconds=300):
    start_time = time.time()

    while time.time() - start_time < timeout_seconds:
        try:
            node = kube_client.read_node(node_name)
            conditions = node.status.conditions
            for condition in conditions:
                if condition.type == "Ready" and condition.status == "True":
                    print(f"Node {node_name} is ready!")
                    return True
        except Exception as e:
            print(f"Error checking node status: {str(e)}")

        time.sleep(5)

    print(f"Timeout: Node {node_name} not ready after {timeout_seconds} seconds.")
    return False

node_list = kube_client.list_node()

for node in node_list.items:
    node_name = node.metadata.name
    print(f"Checking node: {node_name}")
    if wait_for_node_ready(node_name):
        print(f"Do something with the ready node: {node_name}")

