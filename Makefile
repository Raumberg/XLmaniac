# Define the Docker Compose file
COMPOSE_FILE = docker-compose.yml

# Define the Flet app container name
APP_CONTAINER = app

# Define the Python version
PYTHON_VERSION = 3.9

# Define the Docker image name
IMAGE_NAME = xlord/app

# Build the Docker image
build:
    docker build -t $(IMAGE_NAME) --build-arg PYTHON_VERSION=$(PYTHON_VERSION) .

# Run the Docker Compose environment
up:
    docker-compose -f $(COMPOSE_FILE) up -d

# Stop the Docker Compose environment
down:
    docker-compose -f $(COMPOSE_FILE) down

# Run the Flet app in the container
run:
    docker-compose -f $(COMPOSE_FILE) exec $(APP_CONTAINER) python main.py

# Run the Flet app in debug mode
debug:
    docker-compose -f $(COMPOSE_FILE) exec $(APP_CONTAINER) python -m pdb main.py

# Clean up the Docker environment
clean:
    docker-compose -f $(COMPOSE_FILE) rm -fsv
    docker rmi $(IMAGE_NAME)

# Push the Docker image to a registry (e.g., Docker Hub)
push:
    docker tag $(IMAGE_NAME) $(IMAGE_NAME):latest
    docker push $(IMAGE_NAME):latest