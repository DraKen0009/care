# Use the Python 3.11 slim Bullseye base image
FROM python:3.11-slim-bullseye

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PATH /venv/bin:$PATH

# Install system dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \
    build-essential libjpeg-dev zlib1g-dev \
    libpq-dev gettext wget curl gnupg\
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*


# Download and install typst binary
RUN curl -sL https://api.github.com/repos/typst/typst/releases/latest \
    | grep "browser_download_url.*tar.xz" \
    | cut -d : -f 2,3 \
    | tr -d \" \
    | tail -n 1 \
    | wget -qi - \
    && tar -xf typst-x86_64-unknown-linux-musl.tar.xz \
    && rm typst-x86_64-unknown-linux-musl.tar.xz \
    && mv typst-x86_64-unknown-linux-musl/typst /usr/local/bin/typst \
    && chmod +x /usr/local/bin/typst \
    && rm -rf typst-x86_64-unknown-linux-musl

# Set up virtual environment using Pipenv
RUN python -m venv /venv
RUN pip install pipenv

# Copy Pipfile and Pipfile.lock
COPY Pipfile Pipfile.lock ./

# Install dependencies from Pipfile
RUN pipenv install --system --categories "packages dev-packages"

# Copy application files
COPY . /app

# Define healthcheck command
HEALTHCHECK \
  --interval=10s \
  --timeout=5s \
  --start-period=10s \
  --retries=12 \
  CMD ["/app/scripts/healthcheck.sh"]

# Set working directory
WORKDIR /app
