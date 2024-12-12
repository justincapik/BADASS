import requests
import telnetlib
import time

# GNS3 Server details
gns3_server = "http://localhost:3080"

def create_object(option, json):

    # Make API request to create Docker VM template
    response = requests.post(f"{gns3_server}/v2/{option}", json=json)

    if response.status_code == 201:
        print(f"{option} added successfully!")
    else:
        print(f"Failed to add {option} request:", response.text)

def get_id(option, name, id_name):

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

def add_template_node(name, project_id, template_id, x=50, y=50):
    
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

    project_name = "P1"
    create_object("projects", {"name":project_name})

    project_id = get_id("projects", project_name, "project_id")
    open_project(project_id)

    #
    # Create host machine & template
    #

    host_template_name = "host_naali"
    docker_image = {
        "name": host_template_name,  # Template name in GNS3
        "template_type": "docker",  # Specify Docker template type
        "image": "alpine:latest",  # Correct field for Docker image
        "category": "guest",  # Category for GNS3
        "compute_id": "local",  # Assuming you're using local server
        "adapters": 1,  # Number of network adapters
        "console_type": "telnet"  # Console type (telnet, vnc, etc.)
    }
    create_object("templates", docker_image)
    template_id = get_id("templates", host_template_name, "template_id")

    add_template_node(host_template_name, project_id, template_id)
    node_id = get_id(f"projects/{project_id}/nodes", host_template_name, "node_id")

    start_node(project_id, node_id)
    check_node_status(project_id, node_id)

    #
    # Create router machine & template
    # 
    router_template_name = "router_naali"

    docker_image = {
        "name": router_template_name,  # Template name in GNS3
        "template_type": "docker",  # Specify Docker template type
        "image": "frrouting/frr:latest",  # Correct field for Docker image
        "category": "guest",  # Category for GNS3
        "compute_id": "local",  # Assuming you're using local server
        "adapters": 1,  # Number of network adapters
        "console_type": "telnet",  # Console type (telnet, vnc, etc.)
        "symbol": "/symbols/classic/route_switch_processor.svg"
    }
    create_object("templates", docker_image)
    
    template_id = get_id("templates", router_template_name, "template_id")
    add_template_node(router_template_name, project_id, template_id)
    node_id = get_id(f"projects/{project_id}/nodes", router_template_name, "node_id")

    start_node(project_id, node_id)
    check_node_status(project_id, node_id)


    import subprocess

    # Function to parse the docker ps command and get container ID by image name
    def get_container_id_by_image(image_name):
        # Run the docker ps command
        result = subprocess.run(["docker", "ps"], capture_output=True, text=True)

        if result.returncode != 0:
            print("Error executing 'docker ps' command:", result.stderr)
            return None

        # Split the output into lines and process each line
        lines = result.stdout.splitlines()

        # Skip the header line
        for line in lines[1:]:
            columns = line.split()
            
            # The IMAGE is in the second column, CONTAINER ID is in the first column
            container_id = columns[0]
            container_image = columns[1]

            # Check if the image matches
            if container_image == image_name:
                return container_id

        print(f"No container found for image: {image_name}")
        return None

    # Example usage
    image_name = "frrouting/frr:latest"  # Replace with the image name you're looking for
    container_id = get_container_id_by_image(image_name)

    if container_id:
        print(f"Container ID for image {image_name}: {container_id}")
    else:
        print("No matching container found.")

    # Function to run commands inside the Docker container
    def run_commands_in_container(container_id, commands):
        for command in commands:
            try:
                # Run the command inside the Docker container
                result = subprocess.run(
                    ["docker", "exec", container_id] + ["sh", "-c", command],
                    capture_output=True, text=True, check=True
                )
                
                # Print command output
                print(f"Command: {command}")
                print(f"Output:\n{result.stdout}")
                print(f"Error:\n{result.stderr}" if result.stderr else "No error")
            
            except subprocess.CalledProcessError as e:
                print(f"Command failed: {command}")
                print(f"Error: {e.stderr}")

    if container_id:
        print(f"Found container ID: {container_id}")
        
        # List of commands to run inside the container
        commands = [
            "sed -i 's/bgpd=no/bgpd=yes/' /etc/frr/daemons",
            "sed -i 's/ospfd=no/ospfd=yes/' /etc/frr/daemons",
            "sed -i 's/isisd=no/isisd=yes/' /etc/frr/daemons",
        ]
        
        # Run commands inside the Docker container
        run_commands_in_container(container_id, commands)
    else:
        print("No matching container found.")