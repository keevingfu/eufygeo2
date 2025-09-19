#!/bin/bash

# Auto-sync script for EufyGeo2 project
# This script automatically commits and pushes changes to GitHub

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="/Users/cavin/Desktop/dev/eufygeo2"
GITHUB_REPO="https://github.com/keevingfu/eufygeo2.git"
BRANCH="main"

# Load environment variables
if [ -f "${PROJECT_DIR}/.env" ]; then
    source "${PROJECT_DIR}/.env"
fi

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -d "${PROJECT_DIR}" ]; then
    log_error "Project directory not found: ${PROJECT_DIR}"
    exit 1
fi

cd "${PROJECT_DIR}"

# Check if git repository exists
if [ ! -d ".git" ]; then
    log_error "Not a git repository. Please initialize git first."
    exit 1
fi

# Check for changes
if git diff --quiet && git diff --cached --quiet; then
    log_info "No changes detected. Nothing to sync."
    exit 0
fi

log_info "Starting auto-sync process..."

# Get current timestamp
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Generate commit message
if [ $# -eq 0 ]; then
    COMMIT_MSG="auto-sync: updates on ${TIMESTAMP}"
else
    COMMIT_MSG="$1"
fi

# Add all changes
log_info "Adding changes to staging..."
git add .

# Check if there are staged changes
if git diff --cached --quiet; then
    log_warning "No staged changes found after git add."
    exit 0
fi

# Show what will be committed
log_info "Changes to be committed:"
git diff --cached --name-status

# Commit changes
log_info "Committing changes..."
git commit -m "${COMMIT_MSG}

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push to remote
log_info "Pushing to GitHub..."
if git push origin "${BRANCH}"; then
    log_success "Successfully synced to GitHub!"
    log_info "Repository: ${GITHUB_REPO}"
    log_info "Branch: ${BRANCH}"
    log_info "Commit: $(git rev-parse --short HEAD)"
else
    log_error "Failed to push to GitHub. Please check your connection and credentials."
    exit 1
fi

# Optional: Run tests after sync
if [ -f "package.json" ] && command -v npm &> /dev/null; then
    log_info "Running quick health check..."
    if npm run lint --silent > /dev/null 2>&1; then
        log_success "Lint check passed"
    else
        log_warning "Lint check failed - consider running 'npm run lint:fix'"
    fi
    
    if npm run typecheck --silent > /dev/null 2>&1; then
        log_success "Type check passed"
    else
        log_warning "Type check failed - please fix TypeScript errors"
    fi
fi

log_success "Auto-sync completed successfully!"

# Show repository status
echo ""
log_info "Repository Status:"
echo "  📁 Working Directory: ${PROJECT_DIR}"
echo "  🔗 Remote Repository: ${GITHUB_REPO}"
echo "  🌿 Current Branch: $(git branch --show-current)"
echo "  📝 Latest Commit: $(git log -1 --oneline)"
echo "  🕒 Sync Time: ${TIMESTAMP}"