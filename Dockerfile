#########################################
## Importing the current latest python image for NeoGPT
#########################################

FROM python:latest

#########################################

#########################################
## Creating 'app' folder inside container
## where resides the NeoGPT source files
#########################################
WORKDIR /app

#########################################
## Copying source files to app directory
#########################################
COPY . /app/

#########################################
## Installing requirements for The project 
## using pip
#########################################
RUN pip install -r requirements.txt

#########################################
#########################################
RUN python builder.py

CMD [ "python" ,"main.py"]