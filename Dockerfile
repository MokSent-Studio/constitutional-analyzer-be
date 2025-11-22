# --- Stage 1: The Builder ---
# This stage efficiently installs dependencies from our lockfile using uv
FROM python:3.11-slim AS builder

# Install uv system-wide
RUN pip install uv

# Create a virtual environment that uv will install into
# This keeps our final image clean
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy the lockfile first to leverage Docker layer caching
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt

# Use uv to install dependencies from the lockfile.
# This is extremely fast because all versions are pre-resolved.
RUN uv pip install --no-cache-dir -r /code/requirements.txt


# --- Stage 2: The Final Production Image ---
# This stage creates the lean, final container
FROM python:3.11-slim

# Set the environment variable to use the venv we're about to copy
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy the populated virtual environment from the builder stage
COPY --from=builder $VIRTUAL_ENV $VIRTUAL_ENV

# Copy the application source code
WORKDIR /code
COPY ./app /code/app

# Command to run the application using uvicorn.
# It will listen on port 8080, which is the default expected by Cloud Run.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]