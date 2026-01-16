# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build argument for API URL
ARG VITE_API_BASE_URL=/api/v1
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

# Build the application
RUN npm run build

# Production stage with Node.js and serve
FROM node:20-alpine

WORKDIR /app

# Install serve globally for static file serving and wget for healthcheck
RUN npm install -g serve && \
    apk add --no-cache wget

# Copy built files from builder
COPY --from=builder /app/dist ./dist

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost:3000/ || exit 1

# Start serve with SPA routing support (-s flag enables SPA mode for client-side routing)
CMD ["serve", "-s", "dist", "-l", "3000"]

