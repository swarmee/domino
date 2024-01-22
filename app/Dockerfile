# Use an official Python runtime as a parent image
FROM python:3.12

# Set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends gcc

# Install python dependencies
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt


# Run the application:
#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--no-access-log", "--limit-concurrency",  "20", "--workers", "3"]  

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--no-access-log"]  
## Remove --reload to get concurrency to work