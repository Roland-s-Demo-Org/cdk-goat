FROM python:3.7-buster

# Install necessary packages
RUN apt-get update

RUN apt-get install -y wget build-essential libpq-dev python3-dev python3-psycopg2
RUN python -m pip install --upgrade pip setuptools wheel

# Copy and install Python dependencies
RUN mkdir /app
COPY requirements.txt /app

# Set the working directory and copy the application files
WORKDIR /app
RUN python -m pip install -r requirements.txt
COPY run.py /app/
COPY sqli /app/sqli

RUN useradd -U -u 1000 appuser && chown -R 1000:1000 /app
USER 1000

CMD ["python", "run.py"]