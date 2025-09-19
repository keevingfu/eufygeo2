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