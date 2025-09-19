#!/bin/bash

# BMAD-METHOD™ Setup Verification Script for Eufy GEO Project

echo "🚀 Verifying BMAD-METHOD™ Setup for Eufy GEO Project..."
echo ""

# Check Node.js version
echo "1️⃣ Checking Node.js version..."
NODE_VERSION=$(node -v)
REQUIRED_VERSION="v20"

if [[ $NODE_VERSION == $REQUIRED_VERSION* ]]; then
    echo "✅ Node.js $NODE_VERSION installed (v20+ required)"
else
    echo "❌ Node.js version $NODE_VERSION is too old. Please install Node.js v20+"
    echo "   Visit: https://nodejs.org/"
    exit 1
fi

echo ""
echo "2️⃣ Installing BMAD-METHOD™..."

# Check if already installed
if [ -d ".bmad-core" ]; then
    echo "📦 BMAD-METHOD™ already installed, updating..."
    npm run install:bmad
else
    echo "📦 Installing BMAD-METHOD™ for the first time..."
    npx bmad-method install
fi

# Verify installation
echo ""
echo "3️⃣ Verifying installation..."
if [ -d ".bmad-core" ] && [ -f ".bmad-core/agents/analyst.md" ]; then
    echo "✅ BMAD-METHOD™ core files installed successfully"
else
    echo "❌ BMAD-METHOD™ installation failed"
    exit 1
fi

# Check for agents
echo ""
echo "4️⃣ Available BMAD Agents:"
if [ -d ".bmad-core/agents" ]; then
    echo "✅ Found the following agents:"
    ls -1 .bmad-core/agents/*.md | sed 's/.bmad-core\/agents\//  - /g' | sed 's/\.md//g'
fi

# Create example PRD for GEO project
echo ""
echo "5️⃣ Creating example PRD template for GEO project..."
mkdir -p project-docs

cat > project-docs/GEO-PLATFORM-PRD-TEMPLATE.md << 'EOF'
# Product Requirements Document (PRD)
## Eufy GEO Platform

### Executive Summary
AI-powered Generative Engine Optimization platform for Eufy smart home products.

### Business Objectives
- 40% AIO coverage for core keywords in 3 months
- 30% increase in GEO traffic
- 25% increase in Reddit positive mentions
- 10% higher conversion rate vs traditional SEO

### Core Features
1. **Keyword Management System**
   - 850+ keyword database with P0-P4 classification
   - Auto-classification algorithm
   - CSV bulk import/export
   - Real-time AIO status tracking

2. **Content Lifecycle Management**
   - AI-powered content generation
   - Multi-stage approval workflow
   - Version control
   - Multi-channel distribution

3. **Analytics Dashboard**
   - Real-time KPI monitoring
   - ROI attribution
   - Automated reporting
   - Competitive analysis

### Technical Requirements
- Frontend: React + TypeScript + Material-UI
- Backend: Node.js + Express + PostgreSQL
- Caching: Redis
- Queue: Bull/BullMQ
- Performance: <2s response time, 10k concurrent users

### User Personas
1. Business Manager - Executive dashboards
2. SEO Strategist - Keyword management
3. Content Creator - Content creation tools
4. Channel Manager - Distribution management

[Additional sections to be filled by PM agent...]
EOF

cat > project-docs/GEO-ARCHITECTURE-TEMPLATE.md << 'EOF'
# System Architecture Document
## Eufy GEO Platform

### System Overview
Microservices-ready architecture with modular design.

### Technology Stack
- **Frontend**: React 18, TypeScript, Material-UI, ECharts
- **Backend**: Node.js, Express, TypeScript
- **Database**: PostgreSQL 15, Redis 7
- **Queue**: Bull/BullMQ
- **Infrastructure**: Docker, Kubernetes

### Architecture Patterns
- RESTful API design
- Event-driven communication
- Cache-first approach
- Horizontal scalability

### Services
1. **Keyword Service** - Keyword management and classification
2. **Content Service** - Content lifecycle and workflow
3. **Analytics Service** - Data aggregation and reporting
4. **Integration Service** - External API connections

[Additional sections to be filled by Architect agent...]
EOF

echo "✅ Created PRD and Architecture templates in project-docs/"

echo ""
echo "6️⃣ Next Steps:"
echo ""
echo "📌 For Web UI (Planning Phase):"
echo "   1. Create a new Gemini Gem or CustomGPT"
echo "   2. Upload team file from: https://github.com/bmadcode/bmad-method"
echo "   3. Start with: *analyst or #bmad-orchestrator"
echo ""
echo "📌 For IDE (Development Phase):"
echo "   1. Open this project in Cursor/Windsurf/VS Code"
echo "   2. Use *sm --shard-doc to break down PRD into stories"
echo "   3. Use *dev --implement to build features"
echo ""
echo "📌 Quick Commands Reference:"
echo "   *help - Show all commands"
echo "   *analyst - Start requirements analysis"
echo "   *pm --create-prd - Create product requirements"
echo "   *architect --design - Design system architecture"
echo "   #bmad-orchestrator - Ask workflow questions"
echo ""
echo "✅ BMAD-METHOD™ setup complete for Eufy GEO Project!"
echo ""
echo "🔗 Resources:"
echo "   - Documentation: https://github.com/bmadcode/bmad-method"
echo "   - Discord: Join the BMad community for help"
echo "   - YouTube: Subscribe to BMadCode for tutorials"