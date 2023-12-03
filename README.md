## Description

The data scraper API scrapes data using the given query from multiple social media platforms and shopping sites namely reddit, instagram and amazon.

## Install dependencies:

### Create new Virtual Environment:

```bash
python -m venv scraper-app-env
```

### Install the dependencies:

```bash
RUN pip install --no-cache-dir -r requirements.txt
```

## Run the App

Set all the necessary environment variables. Refer .env.example

```bash
python run.py
```

## Deployment

### Build Docker image:

```bash
docker build -t . scraper-app:v1
```

## Run the Docker image

```bash
docker run -p 5000:5000 scraper-app:v1
```