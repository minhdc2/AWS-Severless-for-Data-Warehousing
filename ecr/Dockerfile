# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/engine/reference/builder/

ARG PYTHON_VERSION=3
FROM python:${PYTHON_VERSION} as base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get -y update
RUN pip install --upgrade pip
RUN apt-get install zip -y
RUn apt-get install unzip -y

# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layer.
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# Copy the source code into the container.
COPY . /app/.

# Install chromedriver
ARG CHROMEDRIVER_DIR=/app/connection_config/web_driver
ARG CHROMEDRIVER_ZIPFILE=chromedriver-linux64.zip
ARG SUB_DIR=chromedriver-linux64
RUN wget -N https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/117.0.5938.149/linux64/${CHROMEDRIVER_ZIPFILE} -P ~/
RUN unzip ~/${CHROMEDRIVER_ZIPFILE} -d ~/
RUN rm ~/${CHROMEDRIVER_ZIPFILE}
RUN mv -f ~/${SUB_DIR} ${CHROMEDRIVER_DIR}
RUN chown root:root ${CHROMEDRIVER_DIR}
RUN chmod 0755 ${CHROMEDRIVER_DIR}

# Install chrome broswer
RUN curl -sS -o - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list
RUN apt-get -y update
RUN apt-get -y install google-chrome-stable

# Expose the port that the application listens on.
EXPOSE 5000

# Run the application.
CMD python /app/main.py
