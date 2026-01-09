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

# Build React App with production API URL (empty because endpoints already have /api)
ENV VITE_API_URL=
RUN bun run build
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
    ca-certificates \
    && wget -q -O /tmp/google-chrome-key.pub https://dl-ssl.google.com/linux/linux_signing_key.pub \
    && gpg --dearmor -o /usr/share/keyrings/google-chrome-keyring.gpg /tmp/google-chrome-key.pub \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/* /tmp/google-chrome-key.pub

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
EXPOSE 8000

# Start script: Xvfb + Uvicorn
COPY --chmod=755 start_single_container.sh /app/start.sh

CMD ["/app/start.sh"]
