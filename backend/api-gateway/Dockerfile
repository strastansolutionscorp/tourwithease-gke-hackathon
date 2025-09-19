# Stage 1: Build the application
FROM node:18-alpine AS builder

WORKDIR /app

# Copy all package.json and lerna.json files
COPY lerna.json package.json package-lock.json ./
COPY shared/package.json ./shared/package.json
COPY agents/package.json ./agents/package.json
COPY backend/api-gateway/package.json ./backend/api-gateway/package.json

# Install all dependencies using workspaces
RUN npm install

# Copy the rest of the source code
COPY . .

# Build the api-gateway package
RUN npm run build --workspace=@tourwithease/api-gateway

# Stage 2: Create the production image
FROM node:18-alpine

WORKDIR /app

# Copy the built application and node_modules from the builder stage
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/backend/api-gateway/dist ./backend/api-gateway/dist
COPY --from=builder /app/backend/api-gateway/package.json ./backend/api-gateway/package.json

# Set the working directory to the api-gateway package
WORKDIR /app/backend/api-gateway

# Expose the port the app runs on
EXPOSE 3001

# Start the application
CMD ["node", "dist/index.js"]