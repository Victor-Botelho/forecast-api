FROM python:3.11-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Create the logs directory and base files
RUN mkdir logs
RUN touch logs/access.log
RUN touch logs/error.log

# Upgrade pip to the latest version
RUN pip install --upgrade pip

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the content of the local src directory to the working directory
COPY src/ ./src/

# Copy the Gunicorn config file
COPY gunicorn_config.py .

# Set environment variables
ENV GUNICORN_BIND=0.0.0.0:8000

# Specify the command to run on container start
CMD gunicorn --config gunicorn_config.py src.main:app
