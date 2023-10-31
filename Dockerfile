# Use the latest Python image as the base image
FROM python:3.11

# Set the working directory inside the container
WORKDIR /app-neo

# Copy the current directory contents into the container at /app
COPY . /app-neo/

#Run the dependency installation script as well as builder script to build the database
RUN pip install -r requirements.txt &&  python builder.py

# Specify the command to run on container startup
CMD [ "python" ,"main.py"]

#---------------------------------------------------------#

# Documentation for running the application on containers: 

#---------------------------------------------------------#

#---------------------------------------------------------#
## Build the Docker Image : 

# Run the following command in the directory containing the Dockerfile to build the Docker image.

#> git clone https://github.comneokd/neogpt 
#> cd neopgpt
#! READ docs/builder.md regarding instructions to build database
# Without proper adherence,image might show unexpected failure at build times.
#> docker build -t neogpt .

#---------------------------------------------------------#

## Run the Docker Container:

#After the image is built, you can run a container based on that image:

#> docker run --name neogpt_container -d neopgpt-image

# This spins up a new container in detached mode running your new NeoGPT Application!

#---------------------------------------------------------#

## Interacting with NeoGPT running in container :

#> docker exec -it neogpt_container/bin/bash

# After executing this command, you will be inside the container's shell and can run commands as if you were working directly within the container. This can be useful for debugging, troubleshooting, or running commands that need to be executed within the container's environment.

#---------------------------------------------------------#

## Manage Docker Containers and Images:

# You can manage your Docker containers and images using various commands such as docker ps, docker stop, docker rm, and docker rmi. These commands help you view running containers, stop containers, remove containers, and remove images, respectively.For more info,read docs at https://docs.docker.com/reference/

#---------------------------------------------------------#

## Push Docker Image to a Registry:

# If you want to make your Docker image available to others or deploy it to a remote server, you can push it to a Docker image registry. Popular options include Docker Hub.

##END