#!/bin/bash
# Setup script for Snake Game Docker environment

set -e

echo "🐍 Snake Game - Docker Setup"
echo "============================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        echo "📝 Creating .env file from .env.example..."
        cp .env.example .env
        # Generate a random SECRET_KEY if openssl is available
        if command -v openssl &> /dev/null; then
            SECRET_KEY=$(openssl rand -hex 32)
            # Update SECRET_KEY in .env file (works on both Linux and macOS)
            if [[ "$OSTYPE" == "darwin"* ]]; then
                sed -i '' "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
            else
                sed -i "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
            fi
        fi
        echo "✅ Created .env file from .env.example"
        echo "⚠️  Please review and update SECRET_KEY and POSTGRES_PASSWORD for production!"
    else
        echo "❌ .env.example file not found. Please create .env file manually."
        exit 1
    fi
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🚀 Building and starting Docker containers..."
echo ""

# Build and start containers
docker-compose up --build -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 5

# Check service status
echo ""
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "✅ Setup complete!"
echo ""
echo "📍 Access the application:"
echo "   Frontend:  http://localhost"
echo "   Backend:   http://localhost:8001"
echo "   API Docs:  http://localhost:8001/docs"
echo ""
echo "📝 Useful commands:"
echo "   View logs:     docker-compose logs -f"
echo "   Stop services: docker-compose down"
echo "   Restart:       docker-compose restart"
echo ""

