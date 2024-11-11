FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1

# Install system dependencies (if any required, like build-essential, libpq-dev, etc.)
# RUN apt-get update && apt-get install -y build-essential libpq-dev

WORKDIR /app

# Copy only the requirements first to leverage Docker cache
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application after installing dependencies
COPY . /app/

# Run the Django application (you can uncomment this when you're ready to run)
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
