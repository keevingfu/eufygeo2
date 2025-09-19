# Context Engineering Setup Guide for Eufy GEO Project

## Current State Analysis

### ✅ What You Have

1. **Context Engineering Commands**
   - `/prp-gen` - Generate Product Requirements Prompts
   - `/prp-exec` - Execute PRPs for implementation
   - Project-specific examples in CLAUDE.md

2. **SuperClaude Framework**
   - Full command system with 20+ commands
   - MCP server integration
   - Persona system with 11 specialists
   - Wave orchestration
   - Quality gates and validation

3. **BMAD-METHOD Integration**
   - Agent commands for full development lifecycle
   - Workflow orchestration
   - Agile development support

### ❌ What's Missing for Full Context Engineering

Based on the Context Engineering template, you need to add:

1. **Directory Structure**
   ```
   eufygeo2/
   ├── .claude/
   │   ├── commands/
   │   │   ├── generate-prp.md    # PRP generation command
   │   │   └── execute-prp.md     # PRP execution command
   │   └── settings.local.json    # Claude Code permissions
   ├── PRPs/
   │   ├── templates/
   │   │   └── prp_base.md       # Base template for PRPs
   │   └── [generated PRPs]      # Your generated PRPs go here
   ├── examples/                  # Critical for patterns!
   │   ├── README.md             # Explains each example
   │   ├── neo4j_queries/        # Neo4j query patterns
   │   ├── dashboards/           # Dashboard patterns
   │   ├── api/                  # API patterns
   │   └── tests/                # Test patterns
   ├── INITIAL.md                # Template for feature requests
   └── INITIAL_EXAMPLE.md        # Example feature request
   ```

2. **Command Implementations**
   - Custom `/generate-prp` command
   - Custom `/execute-prp` command
   - These map to your existing `/prp-gen` and `/prp-exec`

3. **Examples Directory**
   - Critical for AI to understand your patterns
   - Should contain real code from your project
   - Include both good and bad examples

## Setup Instructions

### Step 1: Create Directory Structure

```bash
# Create Context Engineering directories
mkdir -p .claude/commands
mkdir -p PRPs/templates
mkdir -p examples/{neo4j_queries,dashboards,api,tests}

# Create settings for Claude Code
cat > .claude/settings.local.json << 'EOF'
{
  "commands": {
    "enabled": true,
    "sources": [".claude/commands"]
  }
}
EOF
```

### Step 2: Create Command Files

Create `.claude/commands/generate-prp.md`:
```markdown
# Generate PRP Command

This command generates a comprehensive Product Requirements Prompt from an INITIAL.md file.

## Process:
1. Read the INITIAL.md file specified in $ARGUMENTS
2. Research the codebase for relevant patterns
3. Search for similar implementations
4. Fetch relevant documentation
5. Create a comprehensive PRP in PRPs/ directory

## Execution:
- Use /analyze to understand codebase patterns
- Use /research --firecrawl for external documentation
- Generate PRP following the template in PRPs/templates/prp_base.md
- Include validation gates and test requirements
- Score confidence level (1-10)
```

Create `.claude/commands/execute-prp.md`:
```markdown
# Execute PRP Command

This command executes a Product Requirements Prompt to implement features.

## Process:
1. Read the PRP file specified in $ARGUMENTS
2. Create detailed task list using TodoWrite
3. Execute each component with validation
4. Run tests and fix issues
5. Ensure all requirements are met

## Execution:
- Use TodoWrite to track progress
- Follow the implementation plan exactly
- Run validation after each major step
- Use appropriate personas for each task
- Iterate until all tests pass
```

### Step 3: Create PRP Template

Create `PRPs/templates/prp_base.md`:
```markdown
# Product Requirements Prompt: [Feature Name]

## Metadata
- **Generated**: [Date]
- **Confidence**: [1-10]
- **Complexity**: [Low/Medium/High]
- **Estimated Time**: [Hours/Days]

## Context
[Comprehensive background and requirements]

## Success Criteria
- [ ] Criteria 1
- [ ] Criteria 2
- [ ] All tests pass
- [ ] Documentation complete

## Implementation Plan

### Phase 1: Setup
1. [Step with validation]
2. [Step with validation]

### Phase 2: Core Implementation
1. [Step with validation]
2. [Step with validation]

### Phase 3: Testing & Documentation
1. [Step with validation]
2. [Step with validation]

## Validation Gates
- After Phase 1: [Test command]
- After Phase 2: [Test command]
- Final validation: [Test command]

## Examples to Follow
- Pattern 1: examples/[file]
- Pattern 2: examples/[file]

## Gotchas & Considerations
- [Important consideration 1]
- [Important consideration 2]
```

### Step 4: Create INITIAL.md Template

Create `INITIAL.md`:
```markdown
## FEATURE:
[Describe what you want to build - be specific about functionality and requirements]

## EXAMPLES:
[List any example files in the examples/ folder and explain how they should be used]

## DOCUMENTATION:
[Include links to relevant documentation, APIs, or MCP server resources]

## OTHER CONSIDERATIONS:
[Mention any gotchas, specific requirements, or things AI assistants commonly miss]
```

### Step 5: Populate Examples Directory

This is CRITICAL! Add real examples from your project:

```bash
# Copy existing patterns to examples
cp eufy-seo-dashboard.html examples/dashboards/
cp neo4j_cypher_queries.cypher examples/neo4j_queries/
cp neo4j_dashboard_server.py examples/api/
cp tests/geo-visibility/*.test.ts examples/tests/

# Create README for examples
cat > examples/README.md << 'EOF'
# Examples Directory

## Purpose
These examples show patterns that should be followed when implementing new features.

## Contents

### neo4j_queries/
- `neo4j_cypher_queries.cypher` - Standard query patterns
- Shows proper indexing, relationship traversal, and performance optimization

### dashboards/
- `eufy-seo-dashboard.html` - Dashboard structure with ECharts
- Shows component organization, data binding, responsive design

### api/
- `neo4j_dashboard_server.py` - Flask API patterns
- Shows error handling, CORS setup, Neo4j connection management

### tests/
- `enhanced-geo-tracker.test.ts` - Playwright test patterns
- Shows async handling, data validation, API mocking

## Usage
When implementing new features, reference these examples for:
1. Code structure and organization
2. Error handling patterns
3. Testing approaches
4. Naming conventions
5. Documentation style
EOF
```

## Using Context Engineering in Your Project

### Example 1: Building a New Dashboard

Create `INITIAL_keyword_dashboard.md`:
```markdown
## FEATURE:
Build a keyword performance dashboard that shows:
- Real-time keyword ranking changes
- AI Overview appearance tracking
- Competitor comparison for each keyword
- Export functionality to CSV/PDF

## EXAMPLES:
- Use examples/dashboards/eufy-seo-dashboard.html for chart structure
- Follow the ECharts pattern for visualizations
- Use the same color scheme and responsive design

## DOCUMENTATION:
- ECharts documentation: https://echarts.apache.org/
- Neo4j query examples in examples/neo4j_queries/
- Flask API patterns in examples/api/

## OTHER CONSIDERATIONS:
- Must handle 1000+ keywords efficiently
- Real-time updates via WebSocket
- Mobile-responsive design required
- Export should include all visible data
```

Then run:
```bash
/generate-prp INITIAL_keyword_dashboard.md
/execute-prp PRPs/keyword_dashboard_prp.md
```

### Example 2: Implementing GEO Tracking

Create `INITIAL_geo_tracking.md`:
```markdown
## FEATURE:
Implement automated GEO (Google AI Overview) tracking system:
- Daily automated checks for 850+ keywords
- Store historical data in Neo4j
- Alert system for ranking changes
- Integration with existing dashboards

## EXAMPLES:
- Use examples/tests/enhanced-geo-tracker.test.ts for SerpAPI integration
- Follow examples/api/neo4j_dashboard_server.py for API structure
- Use existing Neo4j schema patterns

## DOCUMENTATION:
- SerpAPI docs: https://serpapi.com/search-api
- Existing GEO tracking: tests/geo-visibility/README.md
- Neo4j schema: CLAUDE.md (Data Model section)

## OTHER CONSIDERATIONS:
- SerpAPI rate limits: 100 requests/month on free tier
- Must handle API failures gracefully
- Historical data retention: 90 days minimum
- Cost optimization for API calls
```

## Benefits of Full Context Engineering

1. **Consistency**: AI follows your exact patterns
2. **Quality**: Validation gates ensure working code
3. **Speed**: One-pass implementation vs multiple iterations
4. **Completeness**: Nothing gets missed with proper context
5. **Learning**: AI improves with more examples

## Next Steps

1. **Set up the directory structure** (5 minutes)
2. **Create command files** (10 minutes)
3. **Add your best code examples** (30 minutes - this is critical!)
4. **Create your first INITIAL.md** (15 minutes)
5. **Generate and execute your first PRP** (instant results!)

Remember: The quality of your examples directly determines the quality of AI-generated code. Invest time in creating comprehensive examples, and you'll save hours on implementation.