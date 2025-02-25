# Step 1: Build the React app
FROM node:16 AS build

# Set working directory
WORKDIR /app

# Copy package.json and package-lock.json separately for better caching
COPY web-app/package*.json ./

# Install dependencies with frozen lockfile for consistency
RUN npm ci --only=production

# Copy the rest of the frontend code
COPY web-app/ .

# Build the React app for production
RUN npm run build

# Step 2: Serve the React app with Nginx (More Efficient)
FROM nginx:alpine

# Set working directory in Nginx
WORKDIR /usr/share/nginx/html

# Remove the default Nginx static files
RUN rm -rf ./*

# Copy built React files from the build stage
COPY --from=build /app/build .

# Expose port 80
EXPOSE 80

# Start Nginx server
CMD ["nginx", "-g", "daemon off;"]

