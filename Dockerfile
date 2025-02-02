### Dockerfile
FROM python:3.12-slim

# Install dependencies
RUN apt-get update && \
    apt-get install -y gnupg wget curl unzip jq --no-install-recommends \
    fonts-liberation libnss3 libgconf-2-4 libxi6 libxrandr2 libxcursor1 libxcomposite1 \
    libasound2 libxdamage1 libatk1.0-0 libatk-bridge2.0-0 libgtk-3-0 libdrm2 libgbm1 libvulkan1 xdg-utils && \
    rm -rf /var/lib/apt/lists/*

# Install Google Chrome
RUN mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /etc/apt/keyrings/google-chrome.gpg && \
    echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable

# Install latest ChromeDriver using CfT endpoint
RUN CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+\.\d+') && \
    DRIVER_URL=$(curl -s https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json | \
    jq -r --arg ver "$CHROME_VERSION" '.channels.Stable.downloads.chromedriver[] | select(.platform == "linux64") | .url') && \
    wget -q -O /tmp/chromedriver.zip "$DRIVER_URL" && \
    unzip /tmp/chromedriver.zip -d /tmp/ && \
    mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver && \
    rm -rf /tmp/chromedriver.zip /tmp/chromedriver-linux64

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Entry point
CMD ["python", "main.py"]