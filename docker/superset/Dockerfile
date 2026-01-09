FROM apache/superset:latest

USER root

# Install system dependencies if needed (psycopg2 needs libpq-dev, which is usually present)
# Install psycopg2-binary into the python environment
# Bootstrap pip in the venv
RUN /app/.venv/bin/python -m ensurepip --default-pip
# Install psycopg2-binary
RUN /app/.venv/bin/python -m pip install psycopg2-binary

USER superset
