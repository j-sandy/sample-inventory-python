# Use an official Python runtime as a parent image
FROM python:3.11-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install pytest pytest-cov # Install testing dependencies

# Copy the current directory contents into the container at /app
COPY . .

# Create a non-root user to run the application
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Change ownership of the app directory to the appuser
RUN chown -R appuser:appuser /app

# Expose port 8000 for the FastAPI application
EXPOSE 8000

# Switch to the non-root user
USER appuser

# Run the uvicorn server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
