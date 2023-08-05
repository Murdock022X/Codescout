
# Use the python image.
FROM python:3.9 as runtime

# Set the Code Scout Home argument, the application will be moved here.
ARG CODE_SCOUT_HOME="/opt/codescout"

# Set the port for Code Scout.
ARG CODE_SCOUT_PORT="8080"

# Set the UID and GID for the Codescout user.
ARG CODE_SCOUT_UID="50000"
ARG CODE_SCOUT_GID="0"

# Code Scout Home environment variable + make the directory and make working dir.
ENV CODE_SCOUT_HOME=${CODE_SCOUT_HOME}
RUN mkdir ${CODE_SCOUT_HOME}
WORKDIR ${CODE_SCOUT_HOME}

# Make a logs directory in the home directory and create gunicorn log files.
RUN mkdir ./logs
RUN touch ./logs/gunicorn.access.log
RUN touch ./logs/gunicorn.error.log

# Copy the website files into the directory as well as app.py which starts the website.
COPY ./website ./website
COPY ./app.py ./app.py

# Copy requirements into the working directory for a venv.
COPY requirements.txt requirements.txt

# Defines how gunicorn runs.
COPY ./gunicorn_config.py .

# Copy the database setup script into directory.
COPY ./setup-db.py .

# Create a virtual env.
RUN python3 -m venv venv

# Add the virtual env to PATH.
ENV PATH="$CODE_SCOUT_HOME/venv/bin:$PATH"

# Install the required packages.
RUN pip install --no-cache-dir -r requirements.txt

# Expose Code Scout port.
EXPOSE ${CODE_SCOUT_PORT}

# Default command for container.
CMD ["gunicorn", "app:app", "-c", "gunicorn_config.py"]
