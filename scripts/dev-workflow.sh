#!/bin/bash

# Development workflow automation script
# This script provides common development tasks

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_DIR="/Users/cavin/Desktop/dev/eufygeo2"

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

show_help() {
    echo "EufyGeo2 Development Workflow Script"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  setup         - Initial project setup"
    echo "  dev           - Start development server"
    echo "  test          - Run all tests"
    echo "  lint          - Run linter and fix issues"
    echo "  build         - Build the project"
    echo "  sync [msg]    - Sync changes to GitHub"
    echo "  clean         - Clean build artifacts"
    echo "  health        - Check project health"
    echo "  docker        - Build and run Docker container"
    echo "  help          - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 setup"
    echo "  $0 dev"
    echo "  $0 sync \"feat: add new feature\""
    echo "  $0 test"
}

setup_project() {
    log_info "Setting up EufyGeo2 project..."
    
    cd "${PROJECT_DIR}"
    
    # Install dependencies
    log_info "Installing dependencies..."
    npm install
    
    # Setup environment
    if [ ! -f ".env" ]; then
        log_warning ".env file not found. Creating from .env.example..."
        cp .env.example .env
        log_warning "Please update .env file with your configuration"
    fi
    
    # Setup git hooks
    log_info "Setting up git hooks..."
    mkdir -p .git/hooks
    
    # Pre-commit hook
    cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
echo "Running pre-commit checks..."

# Run linter
npm run lint
if [ $? -ne 0 ]; then
    echo "Lint failed. Please fix errors before committing."
    exit 1
fi

# Run type check
npm run typecheck
if [ $? -ne 0 ]; then
    echo "Type check failed. Please fix errors before committing."
    exit 1
fi

echo "Pre-commit checks passed!"
EOF
    
    chmod +x .git/hooks/pre-commit
    
    log_success "Project setup completed!"
}

start_dev() {
    log_info "Starting development server..."
    cd "${PROJECT_DIR}"
    npm run dev
}

run_tests() {
    log_info "Running tests..."
    cd "${PROJECT_DIR}"
    
    # Type check
    log_info "Type checking..."
    npm run typecheck
    
    # Lint check
    log_info "Linting..."
    npm run lint
    
    # Unit tests
    log_info "Running unit tests..."
    npm test
    
    # E2E tests (if Playwright is available)
    if command -v npx playwright &> /dev/null; then
        log_info "Running E2E tests..."
        npm run test:playwright
    fi
    
    log_success "All tests passed!"
}

run_lint() {
    log_info "Running linter..."
    cd "${PROJECT_DIR}"
    npm run lint:fix
    log_success "Linting completed!"
}

build_project() {
    log_info "Building project..."
    cd "${PROJECT_DIR}"
    npm run build
    log_success "Build completed!"
}

sync_project() {
    log_info "Syncing project to GitHub..."
    cd "${PROJECT_DIR}"
    
    local commit_msg="${1:-auto-sync: development updates}"
    
    # Run quick checks before sync
    if ! npm run lint --silent; then
        log_error "Lint check failed. Please fix errors before syncing."
        exit 1
    fi
    
    if ! npm run typecheck --silent; then
        log_error "Type check failed. Please fix errors before syncing."
        exit 1
    fi
    
    ./scripts/auto-sync.sh "${commit_msg}"
}

clean_project() {
    log_info "Cleaning project..."
    cd "${PROJECT_DIR}"
    
    # Remove build artifacts
    rm -rf dist/
    rm -rf build/
    rm -rf .next/
    rm -rf coverage/
    rm -rf test-results/
    rm -rf playwright-report/
    
    # Clean npm cache
    npm cache clean --force
    
    log_success "Project cleaned!"
}

check_health() {
    log_info "Checking project health..."
    cd "${PROJECT_DIR}"
    
    # Check dependencies
    log_info "Checking dependencies..."
    npm audit --audit-level moderate
    
    # Check for outdated packages
    log_info "Checking for outdated packages..."
    npm outdated || true
    
    # Check disk usage
    log_info "Checking disk usage..."
    du -sh node_modules/ 2>/dev/null || log_warning "node_modules not found"
    
    # Check git status
    log_info "Git status:"
    git status --porcelain
    
    log_success "Health check completed!"
}

docker_build() {
    log_info "Building Docker container..."
    cd "${PROJECT_DIR}"
    
    docker build -t eufygeo2:latest .
    
    log_info "Running Docker container..."
    docker run -p 3000:3000 --env-file .env eufygeo2:latest
}

# Main script logic
cd "${PROJECT_DIR}" || {
    log_error "Project directory not found: ${PROJECT_DIR}"
    exit 1
}

case "${1:-help}" in
    setup)
        setup_project
        ;;
    dev)
        start_dev
        ;;
    test)
        run_tests
        ;;
    lint)
        run_lint
        ;;
    build)
        build_project
        ;;
    sync)
        sync_project "$2"
        ;;
    clean)
        clean_project
        ;;
    health)
        check_health
        ;;
    docker)
        docker_build
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        log_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac