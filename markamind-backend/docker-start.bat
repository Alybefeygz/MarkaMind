@echo off
REM MarkaMind Backend Docker Start Script for Windows
REM This script starts the development environment using Docker Compose

echo 🚀 Starting MarkaMind Backend Development Environment...

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

REM Check if docker-compose command exists
docker-compose --version >nul 2>&1
if %errorlevel% equ 0 (
    set COMPOSE_CMD=docker-compose
) else (
    docker compose version >nul 2>&1
    if %errorlevel% equ 0 (
        set COMPOSE_CMD=docker compose
    ) else (
        echo ❌ Docker Compose is not available. Please install Docker Compose.
        pause
        exit /b 1
    )
)

echo 📦 Using compose command: %COMPOSE_CMD%

REM Build and start services
echo 🏗️  Building and starting services...
%COMPOSE_CMD% up --build -d

REM Wait for services to be healthy
echo ⏳ Waiting for services to be ready...
timeout /t 5 /nobreak >nul

REM Check service status
echo 📊 Service Status:
%COMPOSE_CMD% ps

REM Show logs for API service
echo 📝 API Service Logs (last 10 lines):
%COMPOSE_CMD% logs --tail=10 api

echo.
echo ✅ MarkaMind Backend is now running!
echo 🌐 API: http://localhost:8000
echo 🗄️  Database: localhost:5432
echo 🔄 Redis: localhost:6379
echo.
echo 📖 Useful commands:
echo   View logs: %COMPOSE_CMD% logs -f [service-name]
echo   Stop services: %COMPOSE_CMD% down
echo   Restart: %COMPOSE_CMD% restart [service-name]
echo   Access API container: %COMPOSE_CMD% exec api bash
echo.
pause