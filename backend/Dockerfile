# Genlogs backend container — for AWS App Runner.
# See specs/004-deploy.md (D1–D7). Build context is backend/.
#
#   docker build -t genlogs-backend backend/
#   docker run -p 8000:8000 genlogs-backend
#
# D1: slim official Python base.
FROM python:3.12-slim

# Predictable, container-friendly Python runtime.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# D2: copy requirements first so the dependency layer is cached across app changes.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application package (the build context is backend/, so app/ is here).
COPY app ./app

# D3: create and switch to a non-root user; own the workdir.
RUN useradd --create-home --uid 10001 appuser \
    && chown -R appuser:appuser /app
USER appuser

# App Runner injects PORT; default to 8000 for local runs. Documentation only —
# the actual bind is in the start command below.
ENV PORT=8000
EXPOSE 8000

# D4: production start command, binds 0.0.0.0 and honours $PORT (App Runner).
# Shell form so ${PORT:-8000} is expanded by the shell at runtime.
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
