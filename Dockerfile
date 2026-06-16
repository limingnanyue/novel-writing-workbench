FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip3 install --no-cache-dir fastapi uvicorn

# Create app directory
COPY server.py .
COPY static/ static/
COPY tools/ tools/

# Create data directory
RUN mkdir -p /data/chapters

# Environment
ENV HOST=0.0.0.0
ENV PORT=8080
ENV DATA_DIR=/data

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/api/health')" || exit 1

CMD ["python3", "server.py"]
