FROM python:3.10-slim

WORKDIR /app

# Install required packages
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the application code
COPY . .

# Create templates directory
RUN mkdir -p templates

EXPOSE 5000

# Command to run the Flask app
CMD ["python", "app.py"] 