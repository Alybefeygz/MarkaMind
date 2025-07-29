#!/bin/bash

# MarkaMind Backend Docker Start Script
# This script starts the development environment using Docker Compose

echo "🚀 Starting MarkaMind Backend Development Environment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Check if docker-compose command exists
if command -v docker-compose > /dev/null 2>&1; then
    COMPOSE_CMD="docker-compose"
elif command -v docker > /dev/null 2>&1 && docker compose version > /dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
else
    echo "❌ Docker Compose is not available. Please install Docker Compose."
    exit 1
fi

echo "📦 Using compose command: $COMPOSE_CMD"

# Load environment variables if .env file exists
if [ -f .env ]; then
    echo "🔧 Loading environment variables from .env file..."
    export $(cat .env | xargs)
fi

# Build and start services
echo "🏗️  Building and starting services..."
$COMPOSE_CMD up --build -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 5

# Check service status
echo "📊 Service Status:"
$COMPOSE_CMD ps

# Show logs for API service
echo "📝 API Service Logs (last 10 lines):"
$COMPOSE_CMD logs --tail=10 api

echo ""
echo "✅ MarkaMind Backend is now running!"
echo "🌐 API: http://localhost:8000"
echo "🗄️  Database: localhost:5432"
echo "🔄 Redis: localhost:6379"
echo ""
echo "📖 Useful commands:"
echo "  View logs: $COMPOSE_CMD logs -f [service-name]"
echo "  Stop services: $COMPOSE_CMD down"
echo "  Restart: $COMPOSE_CMD restart [service-name]"
echo "  Access API container: $COMPOSE_CMD exec api bash"
echo ""