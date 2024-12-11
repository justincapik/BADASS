import requests

# GNS3 Server details
gns3_server = "http://localhost:3080"

def send_req(option, json):

    # Make API request to create Docker VM template
    response = requests.post(f"{gns3_server}/v2/{option}", json=json)

    if response.status_code == 201:
        print(f"{option} added successfully!")
    else:
        print(f"Failed to add {option} request:", response.text)

def get_req(option, name, id_name):

    # Make API request to create Docker VM template
    response = requests.get(f"{gns3_server}/v2/{option}")

    if response.status_code == 200:
        projects = response.json()
        for project in projects:
            if project["name"] == name:  # Look for project named "P1"
                id = project[id_name]
                print(f"{option} ID for '{name}': {id}")
                return id
        else:
            print(f"{option} '{name}' not found.")
    else:
        print(f"Failed to retrieve {option}: {response.text}")
        if response.status_code == 201:
            print(f"{option} added successfully!")
        else:
            print(f"Failed to add {option} request:", response.text)

def add_template(name, project_id, template_id, x=50, y=50):
    
    # Add the node
    node_data = {
        "name": name,
        "x" : x,
        "y" : y,
    }
    response = requests.post(f"{gns3_server}/v2/projects/{project_id}/templates/{template_id}", json=node_data)

    if response.status_code == 201:
        print("Template node added successfully!")
    else:
        print("Failed to add node:", response.text)

def open_project(project_id):
    # Open the project
    response = requests.post(f"{gns3_server}/v2/projects/{project_id}/open")

    if response.status_code == 200:
        print("Project opened successfully!")
    # else:
    #     print("Failed to open project:", response.json())

def start_node(project_id, node_id):
    start_response = requests.post(f"{gns3_server}/v2/projects/{project_id}/nodes/{node_id}/start", json={})

    if start_response.status_code == 200: 
        print("Node started successfully!")
    else:
        print("Failed to start node:", start_response.text)

def check_node_status(project_id, node_id):
    
    status_response = requests.get(f"{gns3_server}/v2/projects/{project_id}/nodes/{node_id}")

    if status_response.status_code == 200:
        node_status = status_response.json()["status"]
        print(f"Node status: {node_status}")
    else:
        print("Failed to retrieve node status:", status_response.text)

def change_symbol(project_id, node_id, symbol):

    symbol = {
        "symbol": f"/symbols/{symbol}"
    }

    response = requests.put(f"{gns3_server}/v2/projects/{project_id}/nodes/{node_id}",
        json=symbol)

    if response.status_code == 200: 
        print("Symbol changed successfully!")
    else:
        print("Failed to change symbol:", response.text)

if __name__ == '__main__':

    template_name = "alpine_jucapik"
    project_name = "P1"

    node_name = "node_jucapik"

    # Docker image details
    docker_image = {
        "name": template_name,  # Template name in GNS3
        "template_type": "docker",  # Specify Docker template type
        "image": "alpine:latest",  # Correct field for Docker image
        "category": "guest",  # Category for GNS3
        "compute_id": "local",  # Assuming you're using local server
        "adapters": 1,  # Number of network adapters
        "console_type": "telnet"  # Console type (telnet, vnc, etc.)
    }

    send_req("templates", docker_image)

    project = {
        "name": project_name,
    }

    send_req("projects", project)

    project_id = get_req("projects", project_name, "project_id")
    open_project(project_id)
    template_id = get_req("templates", template_name, "template_id")

    add_template("host_jucapik", project_id, template_id)
    
    node_id = get_req(f"projects/{project_id}/nodes", "host_jucapik", "node_id")

    start_node(project_id, node_id)
    check_node_status(project_id, node_id)

    import telnetlib

    # Telnet connection parameters
    host = "127.0.0.1"  # GNS3 server (usually localhost)
    port = 5000         # Device console port from the API

    # Connect to the device
    tn = telnetlib.Telnet(host, port)

    # Sending commands
    tn.write(b"cp /etc/frr/vtysh.conf.sample /etc/frr/vtysh.conf\n")
    tn.write(b"sed -i 's/^bgpd=no/bgpd=yes/' '/etc/frr/daemons'\n")
    tn.write(b"sed -i 's/^ospfd=no/ospfd=yes/' '/etc/frr/daemons'\n")
    tn.write(b"sed -i 's/^isisd=no/isisd=yes/' '/etc/frr/daemons'\n")

    # Close the connection
    tn.close()

    change_symbol(project_id, node_id, "classic/route_switch_processor.svg")
