# Stage 1: Build the application
FROM node:18-alpine AS builder

WORKDIR /app

# Copy all package.json and lerna.json files
COPY lerna.json package.json package-lock.json ./
COPY shared/package.json ./shared/package.json
COPY agents/package.json ./agents/package.json
COPY frontend/my-app/package.json ./frontend/my-app/package.json

# Install all dependencies using workspaces
RUN npm install

# Copy the rest of the source code
COPY . .

# Build the frontend application
RUN npm run build --workspace=my-app

# Stage 2: Create the production image
FROM node:18-alpine

WORKDIR /app

# Copy the built application and node_modules from the builder stage
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/frontend/my-app/.next ./frontend/my-app/.next
COPY --from=builder /app/frontend/my-app/public ./frontend/my-app/public
COPY --from=builder /app/frontend/my-app/package.json ./frontend/my-app/package.json

# Set the working directory to the my-app package
WORKDIR /app/frontend/my-app

# Expose the port the app runs on
EXPOSE 3000

# Start the application
CMD ["npm", "start"]