
# Use Python 3.12 as the base image
FROM python:3.12-alpine

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Create a working directory and set it as the working directory
RUN mkdir /code
WORKDIR /code

# Copy application files to the container
COPY ./server.py .
COPY ./templates ./templates
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Expose the application's port
EXPOSE 5000

# Set the default command to run the application
ENTRYPOINT ["python", "./server.py"]

