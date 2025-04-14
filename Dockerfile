FROM python:3.12-bookworm

WORKDIR /usr/src/app

# Install necessary system packages
RUN apt-get update && apt-get install -y wget unzip

# Copy requirements
COPY requirements.txt .

# Set up virtual environment and install dependencies
RUN python -m venv /venv && \
    /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install -r requirements.txt

# Copy application files
COPY ./app ./app

# Download data if not present (in entrypoint)
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Add venv activation to .bashrc for automatic shell activation
RUN echo 'source /venv/bin/activate' >> /root/.bashrc

ENTRYPOINT ["./entrypoint.sh"]
CMD ["sleep", "infinity"]
