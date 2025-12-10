# NEXUS Deployment Guide

## Prerequisites

- Python 3.10+
- Node.js 18+
- npm or yarn

## Development Setup

### Backend

```bash
# Navigate to backend directory
cd fastapi-backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create . env file (copy from .env.example or create new)
cp .env.example .env

# Run development server
python main.py
# OR
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend runs on:  `http://localhost:8000`

### Frontend

```bash
# Navigate to frontend directory
cd client

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend runs on: `http://localhost:5173`

---

## Production Deployment

### Backend Production

#### Option 1: Gunicorn + Uvicorn Workers

```bash
# Install gunicorn
pip install gunicorn

# Run with multiple workers
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### Option 2: Docker

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["gunicorn", "main:app", "-w", "4", "-k", "uvicorn.workers. UvicornWorker", "--bind", "0.0.0.0:8000"]
```

**Build and run:**
```bash
docker build -t nexus-backend . 
docker run -d -p 8000:8000 --env-file .env nexus-backend
```

### Frontend Production

```bash
# Build for production
npm run build

# Output in dist/ directory
```

#### Serving with Nginx

**nginx.conf:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend static files
    location / {
        root /var/www/nexus/dist;
        try_files $uri $uri/ /index.html;
    }

    # API proxy
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # WebSocket proxy
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
    }
}
```

---

## Docker Compose

**docker-compose. yml:**
```yaml
version: '3.8'

services:
  backend:
    build: 
      context: ./fastapi-backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - DEBUG=false
      - CORS_ORIGINS=["http://localhost:80","https://your-domain.com"]
    restart: unless-stopped

  frontend:
    build: 
      context: ./client
      dockerfile: Dockerfile
    ports: 
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped
```

**Frontend Dockerfile:**
```dockerfile
# Build stage
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

---

## Environment Variables

### Backend (.env)

```bash
# Security
SECRET_KEY=your-super-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Application
APP_NAME=NEXUS AI System
APP_VERSION=1.0.0
DEBUG=false

# CORS (JSON array format)
CORS_ORIGINS=["https://your-domain.com"]

# Simulation
SIMULATION_FPS=12
GRID_SIZE=20
NUM_VEHICLES=8
NUM_EMERGENCY_VEHICLES=2

# CSP
CSP_TICK_INTERVAL=20
TOTAL_POWER=1000

# Bayesian
ACCIDENT_BASE_RATE=0.02
EMERGENCY_SPAWN_RATE=0.01

# XAI
XAI_ENABLED=true
XAI_VERBOSE=false

# Logging
LOG_LEVEL=INFO
```

### Frontend (.env)

```bash
VITE_API_URL=https://api.your-domain.com
VITE_WS_URL=wss://api.your-domain.com
```

---

## SSL/TLS Configuration

### Using Let's Encrypt with Certbot

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com -d api.your-domain.com

# Auto-renewal
sudo certbot renew --dry-run
```

---

## Monitoring

### Health Check Endpoint

```bash
curl http://localhost:8000/
# Response:  {"status": "online", "system": "NEXUS AI Smart City Simulation", ... }
```

### Logging

Backend logs to stdout by default. For production:

```python
# utils/logger.py - Add file handler
file_handler = logging.FileHandler('/var/log/nexus/app.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
```

### Process Management with Systemd

**/etc/systemd/system/nexus-backend.service:**
```ini
[Unit]
Description=NEXUS Backend
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/nexus/fastapi-backend
Environment="PATH=/opt/nexus/fastapi-backend/venv/bin"
ExecStart=/opt/nexus/fastapi-backend/venv/bin/gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable nexus-backend
sudo systemctl start nexus-backend
sudo systemctl status nexus-backend
```

---

## Troubleshooting

### Common Issues

**1. Port already in use:**
```bash
# Find process using port
lsof -i :8000
# Kill process
kill -9 <PID>
```

**2. CORS errors:**
- Check CORS_ORIGINS in backend . env
- Ensure frontend URL is in allowed origins

**3. WebSocket connection failed:**
- Verify backend is running
- Check nginx WebSocket proxy configuration
- Ensure firewall allows WebSocket connections

**4. Module not found:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**5. Frontend build fails:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm run build
```

---

## Scaling Considerations

### Horizontal Scaling

For high traffic, consider:
1. Load balancer (nginx, HAProxy)
2. Multiple backend instances
3. Redis for session/cache sharing
4. PostgreSQL for persistence
5. Message queue (Redis/RabbitMQ) for events

### Performance Optimization

1. **Backend:**
   - Increase worker count based on CPU cores
   - Use Redis for caching
   - Implement database connection pooling

2. **Frontend:**
   - Enable gzip compression
   - Use CDN for static assets
   - Implement lazy loading

3. **WebSocket:**
   - Use Redis pub/sub for multi-instance broadcasting
   - Implement connection pooling