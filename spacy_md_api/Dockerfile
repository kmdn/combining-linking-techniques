# Install the base requirements for the app.
# This stage is to support development.

# docker-compose up --build --remove-orphans
FROM python:3 AS base
WORKDIR /app

# Metadata indicating an image maintainer.
LABEL maintainer="kmdn@github.com"

# install all dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# including spacy's language models for extraction purposes
RUN ["python", "-m", "spacy", "download", "en_core_web_sm"]
#RUN ["python", "-m", "spacy", "download", "en_core_web_trf"]

# copy over our program
COPY md_service.py .

# run program on startup
CMD ["python", "md_service.py"]