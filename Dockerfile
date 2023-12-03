# Use a base image with the necessary dependencies
FROM ubuntu:latest

# Install Python and pip
RUN apt-get update && apt-get install -y python3 python3-pip

# Create a directory for the app
WORKDIR /usr/src/app

# Copy the requirements file and install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Return to the app directory and copy the app files
WORKDIR /usr/src/app
COPY code/src/ .

ARG CACHEBUST=1
RUN python3 processing/downloader.py -d /usr/src/app/data

# Expose the port the app runs on
EXPOSE 8888

# Create a volume for the data 
VOLUME ["/usr/src/app/data"]

# Define the entry point or command to run the app
CMD ["jupyter", "notebook","main.ipynb" ,"--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]

# Build the container using the Dockerfile
# docker build --build-arg CACHEBUST=$(date +%s) -t markowitz .

# Run the container, mounting a host directory to the data volume
# docker run -p 8888:8888 -v /path/to/host/data:/usr/src/app/data markowitz

