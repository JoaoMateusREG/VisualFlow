# ==========================================
# Stage 1: Build Frontend (Node.js)
# ==========================================
FROM node:18-alpine as frontend_build

WORKDIR /app_frontend

# Install dependencies (caching layer)
COPY package*.json ./
RUN npm install

# Build React App
COPY . .
RUN npm run build
# The output will be in /app_frontend/dist

# ==========================================
# Stage 2: Runtime (Python + Chrome)
# ==========================================
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies for Selenium, Chrome, and Xvfb (fake display)
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    xvfb \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install uvicorn fastapi  # Ensure server deps are here

# Create data directories
RUN mkdir -p /app/data /app/workflows /app/logs

# Copy Frontend Build from Stage 1
COPY --from=frontend_build /app_frontend/dist /app/dist

# Copy Backend Code
COPY backend/ /app/backend/

# Set Environment Variables
ENV FRONTEND_DIST_DIR=/app/dist
ENV DATA_DIR=/app/data
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:99

# Expose Port
EXPOSE 8000

# Start script: Xvfb + Uvicorn
COPY --chmod=755 start_single_container.sh /app/start.sh

CMD ["/app/start.sh"]
