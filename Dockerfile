# Use the official Python image from Docker Hub
FROM python:3.11.3-slim

# Set the working directory in the container
WORKDIR /cprapp

# Copy the requirements file into the container
COPY requirements.txt requirements.txt

# Install the dependencies
RUN pip3 install -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Set the environment variable for Flask
ENV FLASK_APP=app.py

# Set the environment variable to run Flask in development mode
ENV FLASK_ENV=development

# Expose the port that the Flask app will run on
EXPOSE 5000

# Run the Gunicorn server
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]

# Run the Flask application
# CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
