#!/bin/bash

# Eufy GEO Platform Setup Script
# This script sets up the complete development environment

echo "🚀 Setting up Eufy GEO Platform..."

# Check prerequisites
command -v node >/dev/null 2>&1 || { echo "❌ Node.js is required but not installed. Aborting." >&2; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "❌ npm is required but not installed. Aborting." >&2; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required but not installed. Aborting." >&2; exit 1; }

# Create project structure
echo "📁 Creating project structure..."
mkdir -p src/{api/{routes,middleware,services,utils},frontend/{components,pages,services,utils},db}
mkdir -p tests/{unit,integration,e2e}
mkdir -p docs/{api,user,technical}
mkdir -p scripts
mkdir -p public/assets

# Initialize package.json if not exists
if [ ! -f package.json ]; then
    echo "📦 Initializing package.json..."
    npm init -y
fi

# Install backend dependencies
echo "📦 Installing backend dependencies..."
npm install express cors helmet morgan dotenv pg redis ioredis
npm install zod multer csv-parser bcryptjs jsonwebtoken
npm install bull bullmq axios node-cron
npm install --save-dev @types/express @types/cors @types/multer @types/bcryptjs
npm install --save-dev @types/jsonwebtoken @types/node typescript ts-node nodemon
npm install --save-dev jest @types/jest supertest @types/supertest

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
npm install react react-dom react-router-dom
npm install @mui/material @mui/icons-material @mui/x-data-grid @mui/x-date-pickers
npm install @emotion/react @emotion/styled
npm install axios echarts react-echarts recharts
npm install @reduxjs/toolkit react-redux
npm install react-hook-form @hookform/resolvers
npm install --save-dev @types/react @types/react-dom @types/react-router-dom
npm install --save-dev @vitejs/plugin-react vite

# Install development tools
echo "📦 Installing development tools..."
npm install --save-dev eslint prettier eslint-config-prettier
npm install --save-dev @typescript-eslint/parser @typescript-eslint/eslint-plugin
npm install --save-dev husky lint-staged
npm install --save-dev @playwright/test

# Create TypeScript configuration
echo "⚙️ Creating TypeScript configuration..."
cat > tsconfig.json << 'EOF'
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020"],
    "jsx": "react-jsx",
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "moduleResolution": "node",
    "allowSyntheticDefaultImports": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "incremental": true,
    "tsBuildInfoFile": "./dist/.tsbuildinfo",
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "tests"]
}
EOF

# Create Vite configuration for frontend
echo "⚙️ Creating Vite configuration..."
cat > vite.config.ts << 'EOF'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src/frontend'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:5001',
        changeOrigin: true,
      },
    },
  },
})
EOF

# Create .env template
echo "⚙️ Creating environment configuration..."
cat > .env.example << 'EOF'
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=eufy_geo
DB_USER=postgres
DB_PASSWORD=postgres

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379

# API Configuration
PORT=5001
NODE_ENV=development

# Security
JWT_SECRET=your-secret-key-here
BCRYPT_ROUNDS=10

# External APIs
SEMRUSH_API_KEY=
AHREFS_API_KEY=
GOOGLE_API_KEY=
YOUTUBE_API_KEY=
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=

# Frontend
REACT_APP_API_URL=http://localhost:5001/api
EOF

# Copy .env.example to .env if not exists
if [ ! -f .env ]; then
    cp .env.example .env
    echo "📄 Created .env file - please update with your actual values"
fi

# Create Docker Compose for PostgreSQL and Redis
echo "🐳 Creating Docker Compose configuration..."
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: eufy-geo-postgres
    environment:
      POSTGRES_DB: eufy_geo
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./src/db/schema.sql:/docker-entrypoint-initdb.d/01-schema.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: eufy-geo-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
  redis_data:
EOF

# Create package.json scripts
echo "📝 Updating package.json scripts..."
npx json -I -f package.json -e 'this.scripts = {
  "dev": "concurrently \"npm run dev:api\" \"npm run dev:frontend\"",
  "dev:api": "nodemon --exec ts-node src/api/server.ts",
  "dev:frontend": "vite",
  "build": "npm run build:api && npm run build:frontend",
  "build:api": "tsc",
  "build:frontend": "vite build",
  "start": "node dist/api/server.js",
  "test": "jest",
  "test:watch": "jest --watch",
  "test:coverage": "jest --coverage",
  "test:e2e": "playwright test",
  "lint": "eslint src --ext .ts,.tsx",
  "format": "prettier --write \"src/**/*.{ts,tsx,js,jsx,json,css,md}\"",
  "db:up": "docker-compose up -d postgres redis",
  "db:down": "docker-compose down",
  "db:migrate": "ts-node scripts/migrate.ts",
  "db:seed": "ts-node scripts/seed.ts"
}'

# Install concurrently for running multiple processes
npm install --save-dev concurrently json

# Create initial API entry point
echo "🚀 Creating initial API entry point..."
cat > src/api/index.ts << 'EOF'
console.log("GEO Platform API starting...");
// Import server from ./server.ts when ready
EOF

# Create initial frontend entry point
echo "🎨 Creating initial frontend entry point..."
cat > src/frontend/main.tsx << 'EOF'
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
EOF

# Create index.html
cat > index.html << 'EOF'
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Eufy GEO Platform</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/frontend/main.tsx"></script>
  </body>
</html>
EOF

# Create basic App component
cat > src/frontend/App.tsx << 'EOF'
import React from 'react'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import KeywordDashboard from './components/KeywordDashboard'

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
  },
})

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <KeywordDashboard />
    </ThemeProvider>
  )
}

export default App
EOF

# Create basic CSS
cat > src/frontend/index.css << 'EOF'
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
EOF

# Create README with instructions
echo "📚 Creating README..."
cat > README-GEO-PLATFORM.md << 'EOF'
# Eufy GEO Platform

## Quick Start

1. **Start the database services:**
   ```bash
   npm run db:up
   ```

2. **Run database migrations:**
   ```bash
   npm run db:migrate
   ```

3. **Start the development servers:**
   ```bash
   npm run dev
   ```

4. **Access the application:**
   - Frontend: http://localhost:3000
   - API: http://localhost:5001
   - API Health: http://localhost:5001/health

## Available Scripts

- `npm run dev` - Start both API and frontend in development mode
- `npm run build` - Build for production
- `npm run test` - Run tests
- `npm run lint` - Lint code
- `npm run format` - Format code

## Architecture

- **Frontend:** React + TypeScript + Material UI + Vite
- **Backend:** Node.js + Express + TypeScript
- **Database:** PostgreSQL + Redis
- **Testing:** Jest + Playwright

## Environment Variables

Copy `.env.example` to `.env` and update the values.
EOF

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update the .env file with your configuration"
echo "2. Start the database: npm run db:up"
echo "3. Run migrations: npm run db:migrate"
echo "4. Start development: npm run dev"
echo ""
echo "For more details, see README-GEO-PLATFORM.md"