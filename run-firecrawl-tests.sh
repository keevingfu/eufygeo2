#!/bin/bash

# Firecrawl Test Runner Script for Eufy SEO Analysis
# This script sets up and runs the Firecrawl integration tests

echo "🚀 Firecrawl Test Suite for Eufy SEO Analysis"
echo "============================================"

# Set environment variables
export FIRECRAWL_API_KEY="fc-7106bd7009b94c8884a082beaecf4294"
export FIRECRAWL_RETRY_MAX_ATTEMPTS="5"
export FIRECRAWL_RETRY_INITIAL_DELAY="2000"
export FIRECRAWL_CREDIT_WARNING_THRESHOLD="2000"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

print_status "Node.js version: $(node -v)"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    print_error "npm is not installed. Please install npm first."
    exit 1
fi

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    print_status "Installing dependencies..."
    npm install
    if [ $? -eq 0 ]; then
        print_success "Dependencies installed successfully"
    else
        print_error "Failed to install dependencies"
        exit 1
    fi
fi

# Install Playwright browsers if needed
if [ ! -d "node_modules/@playwright/test/lib/server" ]; then
    print_status "Installing Playwright browsers..."
    npx playwright install
    if [ $? -eq 0 ]; then
        print_success "Playwright browsers installed successfully"
    else
        print_error "Failed to install Playwright browsers"
        exit 1
    fi
fi

# Create test results directory
mkdir -p test-results

# Function to run tests
run_tests() {
    local test_type=$1
    local test_command=$2
    
    print_status "Running $test_type tests..."
    echo ""
    
    # Run the test command
    eval $test_command
    local test_result=$?
    
    echo ""
    if [ $test_result -eq 0 ]; then
        print_success "$test_type tests completed successfully!"
    else
        print_error "$test_type tests failed with exit code $test_result"
        return $test_result
    fi
}

# Main menu
echo ""
echo "Select test suite to run:"
echo "1) All Firecrawl tests"
echo "2) Basic functionality tests only"
echo "3) SEO analysis tests only"
echo "4) Run tests with UI (interactive)"
echo "5) Run tests in debug mode"
echo "6) Run tests with browser visible"
echo "7) Show test report"
echo "8) Exit"
echo ""

read -p "Enter your choice (1-8): " choice

case $choice in
    1)
        run_tests "all Firecrawl" "npm run test:firecrawl"
        ;;
    2)
        run_tests "basic functionality" "npm run test:firecrawl:basic"
        ;;
    3)
        run_tests "SEO analysis" "npm run test:firecrawl:seo"
        ;;
    4)
        print_status "Launching Playwright UI mode..."
        npm run test:ui
        ;;
    5)
        print_status "Running tests in debug mode..."
        npm run test:debug
        ;;
    6)
        print_status "Running tests with browser visible..."
        npm run test:headed
        ;;
    7)
        print_status "Opening test report..."
        npm run report
        ;;
    8)
        print_status "Exiting..."
        exit 0
        ;;
    *)
        print_error "Invalid choice. Please select 1-8."
        exit 1
        ;;
esac

# After tests complete, offer to show report
if [[ $choice =~ ^[1-3,6]$ ]]; then
    echo ""
    read -p "Would you like to view the test report? (y/n): " view_report
    if [[ $view_report == "y" || $view_report == "Y" ]]; then
        print_status "Opening test report..."
        npm run report
    fi
fi

# Summary
echo ""
echo "============================================"
print_status "Test session completed"
echo ""

# Check if test results exist
if [ -f "test-results/results.json" ]; then
    print_success "Test results saved to: test-results/results.json"
fi

if [ -d "playwright-report" ]; then
    print_success "HTML report available at: playwright-report/index.html"
fi

# Provide next steps
echo ""
echo "Next steps:"
echo "1. Review the test results in the HTML report"
echo "2. Check for any failed tests and debug if needed"
echo "3. Use extracted data for Neo4j import"
echo "4. Monitor Firecrawl API credit usage"
echo ""

print_status "Done!"