
# Use Python 3.12 as the base image
FROM python:3.12

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Install necessary packages and dependencies
RUN apt-get update && \
    apt-get install -y netcat-openbsd gettext httpie && \
    rm -rf /var/lib/apt/lists/*

# Create a working directory and set it as the working directory
RUN mkdir /code
WORKDIR /code

# Copy application files to the container
COPY ./server.py .
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Expose the application's port
EXPOSE 8000

# Set the default command to run the application
ENTRYPOINT ["python", "./server.py"]

