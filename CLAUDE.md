# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## SuperClaude Framework Configuration

This project inherits all capabilities from the global SuperClaude framework configuration.

### Installation & Setup

#### 1. Context Engineering Capability
```bash
# Clone and setup Context Engineering
git clone https://github.com/coleam00/Context-Engineering-Intro.git
cd Context-Engineering-Intro
```

#### 2. BMAD-METHOD™ Automated Development Framework

BMAD-METHOD™ (Breakthrough Method of Agile AI-Driven Development) v4.43.1 - Transform development with specialized AI expertise through agentic agile driven development.

##### Installation Options
```bash
# Option 1: Quick install (recommended)
npx bmad-method install

# Option 2: Install with specific team configuration
npx bmad-method@stable install --team fullstack --ide cursor

# Option 3: Clone and build
git clone https://github.com/bmadcode/bmad-method.git
cd bmad-method
npm run install:bmad

# Update existing installation
git pull
npm run install:bmad

# Install enhanced version
npm i @cloudkinetix/bmad-enhanced
```

##### Prerequisites
- Node.js v20+ required
- Compatible IDEs: Cursor, Windsurf, VS Code, or any IDE with AI chat

##### Two-Phase Workflow

**Phase 1: Agentic Planning (Web UI)**
1. Create PRD with Analyst and PM agents
2. Design architecture with Architect agent  
3. Optional: UX design with UX-Expert agent
4. Human-in-the-loop refinement

**Phase 2: Context-Engineered Development (IDE)**
1. Scrum Master creates hyper-detailed stories
2. Dev agent implements with full context
3. QA agent validates and tests
4. Continuous iteration

##### Core BMAD Agents
- **Orchestrator** (`#bmad-orchestrator`) - Central coordination and guidance
- **Analyst** (`*analyst`) - Requirements analysis and briefs
- **PM** (`*pm`) - Product management and PRD creation
- **Architect** (`*architect`) - System design and architecture
- **Scrum Master** (`*sm`) - Story creation and sprint management
- **Developer** (`*dev`) - Code implementation
- **QA** (`*qa`) - Testing and quality assurance
- **UX-Expert** (`*ux-expert`) - UI/UX design
- **PO** (`*po`) - Product ownership and prioritization
- **DevOps** (`*devops`) - Infrastructure and deployment

##### Quick Start Commands
```bash
# In Web UI (Gemini/CustomGPT)
*help                    # Show all available commands
*analyst                 # Start with requirements analysis
#bmad-orchestrator      # Ask questions about workflow

# In IDE after planning
*sm --shard-doc         # Break down PRD into stories
*sm --create-story      # Create individual story
*dev --implement        # Implement the story
*qa --test             # Test the implementation
```

#### 3. SuperClaude Capabilities
```bash
# Install and upgrade SuperClaude
pipx install SuperClaude && pipx upgrade SuperClaude && SuperClaude install
```

### Core Framework Components
- **COMMANDS.md** - Command execution framework with wave orchestration
- **FLAGS.md** - Flag system with auto-activation and conflict resolution
- **PRINCIPLES.md** - Core development principles and philosophy
- **RULES.md** - Actionable operational rules
- **MCP.md** - Model Context Protocol server integration
- **PERSONAS.md** - Domain-specific AI personas
- **ORCHESTRATOR.md** - Intelligent routing system
- **MODES.md** - Operational modes (Task, Introspection, Token Efficiency)
- **TMUX-ORCHESTRATOR.md** - Multi-agent coordination for 24/7 operation

### Extended Capabilities
- **CONTEXT-ENGINEERING.md** - PRP methodology for one-pass implementation
- **BMAD-METHOD.md** - Agile AI-driven development framework
- **MCP-EXTENDED.md** - Additional MCP servers (Puppeteer, Filesystem, Memory, GitHub, SQLite, Firecrawl)

### Available Commands

#### Development Commands
- `/build` - Project builder with framework detection
- `/implement` - Feature and code implementation
- `/design` - Design orchestration

#### Analysis Commands
- `/analyze` - Multi-dimensional code and system analysis
- `/troubleshoot` - Problem investigation
- `/explain` - Educational explanations

#### Quality Commands
- `/improve` - Evidence-based code enhancement
- `/cleanup` - Project cleanup and technical debt reduction

#### Other Commands
- `/document` - Documentation generation
- `/estimate` - Evidence-based estimation
- `/task` - Long-term project management
- `/test` - Testing workflows
- `/git` - Git workflow assistant
- `/workflow` - Workflow design and automation

### Available Flags

#### Thinking Flags
- `--think` - Multi-file analysis (~4K tokens)
- `--think-hard` - Deep architectural analysis (~10K tokens)
- `--ultrathink` - Critical system redesign analysis (~32K tokens)

#### Efficiency Flags
- `--uc` / `--ultracompressed` - 30-50% token reduction
- `--validate` - Pre-operation validation
- `--safe-mode` - Maximum validation with conservative execution

#### MCP Server Flags
- `--c7` / `--context7` - Enable Context7 for library documentation
- `--seq` / `--sequential` - Enable Sequential for complex analysis
- `--magic` - Enable Magic for UI components
- `--play` / `--playwright` - Enable Playwright for testing
- `--all-mcp` - Enable all MCP servers

#### Wave & Delegation Flags
- `--wave-mode [auto|force|off]` - Control wave orchestration
- `--delegate [files|folders|auto]` - Enable sub-agent delegation
- `--loop` - Enable iterative improvement mode

### Available Personas
- `--persona-architect` - Systems architecture specialist
- `--persona-frontend` - UX specialist, accessibility advocate
- `--persona-backend` - Reliability engineer, API specialist
- `--persona-analyzer` - Root cause specialist
- `--persona-security` - Threat modeler, vulnerability specialist
- `--persona-mentor` - Knowledge transfer specialist
- `--persona-refactorer` - Code quality specialist
- `--persona-performance` - Optimization specialist
- `--persona-qa` - Quality advocate, testing specialist
- `--persona-devops` - Infrastructure specialist
- `--persona-scribe=lang` - Professional writer, documentation specialist

### MCP Servers

#### Core MCP Servers
- **Context7** - Documentation, patterns, best practices
- **Sequential** - Complex analysis, multi-step reasoning
- **Magic** - UI component generation, design systems
- **Playwright** - E2E testing, performance monitoring

#### Extended MCP Servers
- **Puppeteer** - Browser automation, visual testing
- **Filesystem** - Advanced file operations
- **Memory** - Knowledge graph persistence
- **GitHub** - Version control integration
- **SQLite** - Local database operations
- **Firecrawl** - Web scraping and research

### Context Engineering Integration

Generate perfect prompts in one pass:
```bash
# Generate comprehensive prompt
/prp-gen "Build a real-time analytics dashboard"

# Execute with optimal configuration
/prp-exec --file generated_prp.md
```

### BMAD-METHOD™ Integration

#### GEO Platform BMAD Workflow

##### Phase 1: Planning (Web UI)
```bash
# Step 1: Requirements Analysis
*analyst
# Analyze the three GEO requirement documents
# Create initial brief and project understanding

# Step 2: Product Requirements Document
*pm --create-prd
# Generate comprehensive PRD for GEO platform
# Include keyword management, content lifecycle, analytics

# Step 3: Architecture Design
*architect --design
# Design microservices architecture
# Plan database schema and API structure

# Step 4: UX Design (Optional)
*ux-expert
# Create dashboard mockups
# Design user workflows
```

##### Phase 2: Development (IDE)
```bash
# Step 1: Story Creation
*sm --shard-doc PRD.md
# Break down PRD into implementable stories

# Step 2: Sprint Planning
*sm --create-story "Keyword Management API"
*sm --create-story "Dashboard Frontend"
*sm --create-story "Analytics Engine"

# Step 3: Implementation
*dev --implement story-001-keyword-api.md
# Dev agent implements with full context

# Step 4: Testing
*qa --test story-001-keyword-api.md
# QA agent creates and runs tests

# Step 5: DevOps
*devops --deploy
# Setup CI/CD and deployment
```

#### Available BMAD Commands

##### Planning Commands (Web UI)
- `*analyst` - Requirements analysis and elicitation
- `*pm` - Product management and PRD creation
- `*architect` - System architecture and design
- `*ux-expert` - UX/UI design and mockups
- `*po` - Product ownership and backlog

##### Development Commands (IDE)
- `*sm` - Scrum master for story creation
- `*dev` - Developer for implementation
- `*qa` - Quality assurance and testing
- `*devops` - Infrastructure and deployment
- `#bmad-orchestrator` - Ask questions about workflow

##### Task-Specific Commands
- `*create-doc` - Create structured documentation
- `*shard-doc` - Break down documents into stories
- `*advanced-elicitation` - Deep requirements gathering
- `*review-story` - Review user stories
- `*qa-gate` - Quality checkpoint
- `*test-design` - Design test strategies

#### BMAD + GEO Integration Examples

##### Example 1: Creating Keyword Management Module
```bash
# Web UI Phase
*analyst
"I need to analyze requirements for a keyword management system that handles 850+ SEO keywords with P0-P4 classification"

*pm --create-prd
"Create PRD for keyword management with CSV import, auto-classification, and real-time AIO tracking"

*architect --design
"Design PostgreSQL schema and REST API for keyword management with Redis caching"

# IDE Phase
*sm --shard-doc keyword-management-prd.md
# Creates multiple story files

*dev --implement story-001-keyword-schema.md
# Implements database schema

*dev --implement story-002-keyword-api.md  
# Implements REST API

*qa --test story-002-keyword-api.md
# Creates and runs API tests
```

##### Example 2: Analytics Dashboard Development
```bash
# Planning
*ux-expert
"Design analytics dashboard showing KPIs, pyramid visualization, and ROI tracking"

*architect
"Design real-time architecture with WebSockets and ECharts integration"

# Implementation
*sm --create-story "Real-time Analytics Dashboard"
*dev --implement story-analytics-dashboard.md
*qa --test story-analytics-dashboard.md
```

#### BMAD Best Practices for GEO Project

1. **Always Start with Planning Phase**
   - Use Web UI agents to create comprehensive PRD and Architecture
   - Don't skip directly to development

2. **Maintain Context Through Story Files**
   - Stories contain full context from PRD and Architecture
   - Dev agents have everything needed in the story file

3. **Use Orchestrator for Guidance**
   - Type `#bmad-orchestrator` anytime to ask workflow questions
   - Get help understanding the two-phase approach

4. **Leverage Agent Specialization**
   - Let Analyst focus on requirements
   - Let PM create structured PRDs
   - Let Architect design systems properly

### GEO Project Specific Capabilities

#### Context Engineering for GEO
```bash
# Generate PRP for GEO platform components
/prp-gen "Build keyword management system for 850+ keywords with AIO tracking"
/prp-gen "Create content lifecycle management with AI integration"
/prp-gen "Design analytics dashboard for ROI tracking"

# Execute PRP documents
/prp-exec --file prp-eufy-geo-platform.md
/prp-exec --file prp-keyword-management.md
```

#### BMAD Workflow for GEO Development
```bash
# Phase 1: Analysis & Planning
/analyst --research "GEO platform requirements from documents"
/architect --design "microservices architecture for GEO platform"
/pm --create-prd "Eufy GEO Platform MVP"

# Phase 2: Implementation
/sm --create-stories "keyword management module"
/dev --implement "keyword classification algorithm"
/qa --test-plan "GEO platform integration testing"

# Phase 3: Deployment
/devops --setup "AWS infrastructure for GEO platform"
/ux-expert --review "dashboard usability"
```

#### SuperClaude Commands for GEO
```bash
# Analyze existing SEO data
/analyze @eufy-competitor-organic-us-202509.csv --seq --persona-analyzer

# Build GEO dashboards
/build geo-dashboard --magic --c7 --persona-frontend

# Implement keyword tracking
/implement keyword-tracking --seq --c7 --persona-backend

# Research competitor strategies
/research --firecrawl deep --query "smart home SEO strategies 2024"

# Optimize for performance
/improve neo4j_cypher_queries.cypher --persona-performance --focus performance
```

## Project Overview

This is a **Neo4j-based SEO competitive analysis system** for Eufy that imports and analyzes competitor organic search data. It provides graph-based insights into keyword rankings, traffic patterns, and SEO opportunities through multiple dashboard interfaces.

## Commands

### Setup and Run
```bash
# Complete setup (Docker + Neo4j + Data Import)
./setup_neo4j.sh
# Then select option 8 for complete setup

# Launch the dashboard (includes Neo4j start and server)
./launch_dashboard.sh

# Manual steps:
docker-compose up -d                    # Start Neo4j
python3 import_competitor_data_to_neo4j.py   # Import CSV data
python3 neo4j_dashboard_server.py      # Start dashboard API server (port 5001)
```

### Development
```bash
# Install Python dependencies
pip install -r requirements.txt

# Run specific dashboard servers
python3 eufy-seo-dashboard-server.py   # Alternative dashboard server

# Stop services
docker-compose down

# View Neo4j logs
docker-compose logs -f neo4j

# Access Neo4j Browser
open http://localhost:7474

# Quick Neo4j connection test
docker exec eufy-seo-neo4j cypher-shell -u neo4j -p eufyseo2024 "MATCH (n) RETURN COUNT(n) AS total_nodes;"
```

## Architecture

### Data Model (Neo4j Graph)
- **Nodes**: 
  - `Keyword`: text, search_volume, difficulty, cpc, competition, num_results
  - `URL`: address, domain
  - `Domain`: name
  - `Intent`: type (informational, navigational, transactional, commercial)
  - `SERPFeature`: name (featured snippet, people also ask, etc.)
  
- **Relationships**: 
  - `RANKS_FOR` (Keyword→URL): position, previous_position, traffic, traffic_percent, traffic_cost, timestamp
  - `BELONGS_TO` (URL→Domain)
  - `HAS_INTENT` (Keyword→Intent)
  - `HAS_SERP_FEATURE` (Keyword→SERPFeature)

### Components
1. **Neo4j Database** (v5.13.0): 
   - Bolt protocol: port 7687
   - HTTP/Browser: port 7474
   - APOC procedures enabled
   - Memory: 2GB heap, 1GB pagecache

2. **Data Import** (`import_competitor_data_to_neo4j.py`):
   - Batch processing with progress tracking
   - Incremental or full refresh modes
   - Data validation and error handling

3. **API Servers**:
   - `neo4j_dashboard_server.py`: Main Flask API (port 5001)
   - `eufy-seo-dashboard-server.py`: Alternative dashboard server
   - CORS enabled for frontend integration

4. **Dashboard Interfaces**:
   - `eufy-seo-dashboard.html`: Main SEO strategy dashboard with ECharts visualizations
   - `neo4j-seo-dashboard.html`: Neo4j-focused analytics dashboard
   - `eufy-seo-battle-dashboard.html`: Competitive comparison interface
   - `eufy-geo-content-strategy.html`: Geographic content strategy planner

### Access Credentials
- Neo4j: username `neo4j`, password `eufyseo2024`
- Dashboard API: http://localhost:5001
- Neo4j Browser: http://localhost:7474

## Key Cypher Queries

Essential queries are stored in `neo4j_cypher_queries.cypher` and documented in `neo4j_quick_queries.md`:

```cypher
# Data overview
MATCH (n) RETURN labels(n)[0] AS type, COUNT(n) AS count ORDER BY count DESC;

# Top competitors by keyword coverage
MATCH (d:Domain)<-[:BELONGS_TO]-(u:URL)<-[r:RANKS_FOR]-(k:Keyword)
WITH d.name AS competitor, COUNT(DISTINCT k) AS keywords, SUM(r.traffic) AS traffic
RETURN competitor, keywords, traffic ORDER BY keywords DESC LIMIT 10;

# High-value keyword opportunities
MATCH (k:Keyword) WHERE k.search_volume > 5000 AND k.difficulty < 40
AND NOT EXISTS { MATCH (k)-[r:RANKS_FOR]->(u:URL) WHERE r.position <= 10 }
RETURN k.text, k.search_volume, k.difficulty ORDER BY k.search_volume DESC;
```

## Data Files

- **Input**: CSV files matching pattern `eufy*competitor*organic*.csv` or `eufy*organic*positions*.csv`
- **Required columns**: keyword, url, position, traffic, search_volume, difficulty, intent, serp_features
- **Storage**: Neo4j data persisted in `./db/data/`

## Testing Approach

1. **Database connectivity**: 
   ```bash
   docker exec eufy-seo-neo4j cypher-shell -u neo4j -p eufyseo2024 "RETURN 1;"
   ```

2. **Data import verification**: 
   ```bash
   # Check node counts
   docker exec eufy-seo-neo4j cypher-shell -u neo4j -p eufyseo2024 \
     "MATCH (n) RETURN labels(n)[0] AS type, COUNT(n) AS count;"
   ```

3. **API endpoints**:
   ```bash
   # Test API endpoints
   curl http://localhost:5001/api/overview
   curl http://localhost:5001/api/competitors
   curl http://localhost:5001/api/keywords/opportunities
   ```

4. **Dashboard access**: Open dashboards in browser and verify data loading

## Troubleshooting

- **Neo4j won't start**: Check Docker memory allocation (needs 4GB+)
- **Import fails**: Verify CSV file exists and has correct columns
- **Dashboard shows no data**: Check API server is running and Neo4j has data
- **Connection refused**: Ensure Neo4j is healthy: `docker-compose ps`

## Project-Specific Usage Examples

### SEO Analysis with SuperClaude
```bash
# Analyze competitor SEO strategies
/analyze --seq --persona-analyzer --focus seo

# Build SEO dashboard improvements
/build dashboard --magic --c7 --persona-frontend

# Research competitor content strategies
/research --firecrawl deep --query "eufy competitors content strategy"

# Optimize Neo4j queries
/improve neo4j_cypher_queries.cypher --persona-performance --focus performance
```

### Automated Development Workflow
```bash
# Plan new SEO features
/task seo-features --wave-mode auto --persona-architect

# Implement keyword tracking
/implement keyword-tracking --seq --c7 --persona-backend

# Generate comprehensive documentation
/document --persona-scribe=en --c7

# Run full test suite
/test full-stack --puppeteer --playwright --persona-qa
```

### Quality Gates & Validation

All operations follow an 8-step validation cycle:
1. **Syntax validation** - Language parsers, Context7 validation
2. **Type checking** - Sequential analysis, type compatibility  
3. **Lint checking** - Context7 rules, quality analysis
4. **Security scanning** - Sequential analysis, vulnerability assessment
5. **Test execution** - Playwright E2E, coverage analysis (≥80% unit, ≥70% integration)
6. **Performance validation** - Sequential analysis, benchmarking
7. **Documentation check** - Context7 patterns, completeness validation
8. **Integration testing** - Playwright testing, deployment validation

### Resource Management Thresholds

- **Green Zone (0-60%)**: Full operations, predictive monitoring
- **Yellow Zone (60-75%)**: Resource optimization, caching, suggest --uc
- **Orange Zone (75-85%)**: Warning alerts, defer non-critical operations
- **Red Zone (85-95%)**: Force efficiency modes, block resource-intensive
- **Critical Zone (95%+)**: Emergency protocols, essential operations only

### Wave System Auto-Activation

Wave orchestration automatically activates when:
- Complexity score ≥ 0.7
- Files > 20
- Operation types > 2

Wave strategies:
- **progressive**: Iterative enhancement for incremental improvements
- **systematic**: Comprehensive methodical analysis
- **adaptive**: Dynamic configuration based on complexity
- **enterprise**: Large-scale orchestration for >100 files

### Project-Specific Firecrawl Integration

```bash
# Analyze competitor websites
/research --firecrawl crawl --url https://www.arlo.com --depth 3

# Extract structured data from competitors
/research --firecrawl extract --urls competitor-urls.txt --schema product-schema.json

# Generate competitive intelligence report
/research --firecrawl deep --query "security camera market trends 2024"
```

### GEO Optimization Commands

```bash
# Comprehensive GEO analysis
/analyze @content --geo-visibility --seq --firecrawl

# Create GEO-optimized content
/implement geo-content --persona-scribe --magic --c7

# Monitor AI Overview appearances
/test geo-tracking --serpapi --compare-baseline

# Generate GEO strategy
/document geo-strategy --format executive-summary --persona-architect
```