# Use an official Python runtime as a parent image
# We are updating this line to use the 'bookworm' version, which has the correct SSL library
FROM python:3.9-slim-bookworm

LABEL authors="riyakalra"
# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code (e.g., main.py, .env) into the container
COPY . .

# Command to run your FastAPI app when the container launches
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]