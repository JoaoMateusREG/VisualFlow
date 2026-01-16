# ==========================================
# Stage 1: Build Frontend (Bun)
# ==========================================
FROM oven/bun:1 as frontend_build

WORKDIR /app_frontend

# Install dependencies (caching layer)
COPY package.json bun.lock* ./
RUN bun install

# Copy source code
COPY src ./src
COPY public ./public
COPY index.html ./
COPY vite.config.ts ./
COPY tsconfig.json ./
COPY tsconfig.node.json ./
COPY tailwind.config.cjs ./
COPY postcss.config.cjs ./

RUN bun run build
# The output will be in /app_frontend/dist

# ==========================================
# Stage 2: Runtime (Python + Chrome)
# ==========================================
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies for Selenium, Chromium, and Xvfb (fake display)
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    xvfb \
    ca-certificates \
    chromium \
    chromium-driver \
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

# Copy example workflows
COPY backend/workflows/saved/ /app/backend/workflows/saved/

# Set Environment Variables
ENV FRONTEND_DIST_DIR=/app/dist
ENV DATA_DIR=/app/data
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:99

# Expose Port
EXPOSE 8164

# Start script: Xvfb + Uvicorn
COPY --chmod=755 start_single_container.sh /app/start.sh

CMD ["/app/start.sh"]
