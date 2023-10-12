# Select the base image that is best for our application
FROM python:3.10-bullseye
RUN python -m pip install --upgrade pip

# Set the working directory to copy stuff to
WORKDIR /app

# Copy all the code from the local directory into the image
COPY requirements.txt requirements.txt
COPY main.py main.py
COPY queries queries
COPY routers routers

# Install any language dependencies
RUN python -m pip install -r requirements.txt

# !! PORT env var needs to match with exposed port in caprover dashboard
CMD uvicorn main:app --reload --host 0.0.0.0 --port 80
