# Multi-stage build for production optimization
FROM node:20-alpine AS base

# Install dependencies only when needed
FROM base AS deps
WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV PORT=3000

# Create non-root user
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 eufygeo

# Copy built application
COPY --from=builder --chown=eufygeo:nodejs /app/dist ./dist
COPY --from=deps --chown=eufygeo:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=eufygeo:nodejs /app/package.json ./package.json

# Copy any static assets
COPY --chown=eufygeo:nodejs public ./public

USER eufygeo

EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node healthcheck.js

CMD ["npm", "start"]