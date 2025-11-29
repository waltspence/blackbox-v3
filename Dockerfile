# Use an official Python runtime as a parent image
# Slim variant reduces image size (~150MB vs ~800MB)
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Prevent Python from writing pyc files to disc
# and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies (needed for some math/pandas libs)
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Create a volume for the Firebase credentials (optional, safer than copying in)
VOLUME ["/app/secrets"]

# Default command: Run the Discord Bot
# (You can override this to run the analysis script via: docker run ... python scripts/ingest.py)
CMD ["python", "bot.py"]
