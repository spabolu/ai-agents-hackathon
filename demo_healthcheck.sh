#!/bin/bash
# ==============================================================================
# DEMO HEALTH CHECK - AI Agents Hackathon
# ==============================================================================
# Purpose: Quick verification that demo environment is ready
# Usage: ./demo_healthcheck.sh
# Run this 2-3 minutes before demo to verify everything works
# ==============================================================================

# ANSI color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# ==============================================================================
# CONFIGURATION
# ==============================================================================

API_BASE="http://localhost:8000"
REQUIRED_FILES=("main.py" "test_business_logic.py" ".env" "requirements.txt")
PASS_COUNT=0
FAIL_COUNT=0

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

print_header() {
    echo ""
    echo -e "${BOLD}${CYAN}$1${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

check_pass() {
    echo -e "${GREEN}  ✅ $1${NC}"
    ((PASS_COUNT++))
}

check_fail() {
    echo -e "${RED}  ❌ $1${NC}"
    ((FAIL_COUNT++))
}

check_warning() {
    echo -e "${YELLOW}  ⚠️  $1${NC}"
}

# ==============================================================================
# HEALTH CHECKS
# ==============================================================================

clear

cat << 'EOF'
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║                    🏥 DEMO HEALTH CHECK - PRE-FLIGHT 🏥                   ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
EOF

echo ""
echo -e "${CYAN}Running pre-demo health checks...${NC}"
echo ""

# ==============================================================================
# CHECK 1: Required Files
# ==============================================================================

print_header "1️⃣  Required Files"

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        check_pass "$file exists"
    else
        check_fail "$file is missing!"
    fi
done

# ==============================================================================
# CHECK 2: Python Environment
# ==============================================================================

print_header "2️⃣  Python Environment"

if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    check_pass "Python $PYTHON_VERSION installed"
else
    check_fail "Python 3 not found!"
fi

if [ -d ".venv" ]; then
    check_pass "Virtual environment exists (.venv)"
else
    check_fail "Virtual environment not found!"
fi

# ==============================================================================
# CHECK 3: Dependencies
# ==============================================================================

print_header "3️⃣  Dependencies"

if [ -d ".venv" ]; then
    source .venv/bin/activate 2>/dev/null

    REQUIRED_PACKAGES=("fastapi" "uvicorn" "httpx" "openai" "pydantic")

    for package in "${REQUIRED_PACKAGES[@]}"; do
        if python -c "import $package" 2>/dev/null; then
            check_pass "$package installed"
        else
            check_fail "$package not installed!"
        fi
    done
else
    check_fail "Cannot check dependencies - venv not found"
fi

# ==============================================================================
# CHECK 4: Environment Configuration
# ==============================================================================

print_header "4️⃣  Environment Configuration"

if [ -f ".env" ]; then
    check_pass ".env file exists"

    # Check DEMO_MODE
    DEMO_MODE=$(grep -E "^DEMO_MODE=" .env | cut -d '=' -f2)
    if [ "$DEMO_MODE" = "True" ]; then
        check_pass "DEMO_MODE=True (fast demo responses enabled)"
    else
        check_warning "DEMO_MODE=$DEMO_MODE (should be 'True' for demo)"
    fi

    # Check API keys
    REQUIRED_KEYS=("TRUEFOUNDRY_API_KEY" "LINKUP_API_KEY" "FREEPIK_API_KEY")
    for key in "${REQUIRED_KEYS[@]}"; do
        if grep -q "^$key=" .env && [ -n "$(grep "^$key=" .env | cut -d '=' -f2)" ]; then
            check_pass "$key is set"
        else
            check_warning "$key not set (DEMO_MODE will compensate)"
        fi
    done
else
    check_fail ".env file not found!"
fi

# ==============================================================================
# CHECK 5: Server Status
# ==============================================================================

print_header "5️⃣  Server Status"

if curl -s "$API_BASE/" > /dev/null 2>&1; then
    check_pass "Server is running at $API_BASE"

    # Test health endpoint
    HEALTH_RESPONSE=$(curl -s "$API_BASE/")
    if [ -n "$HEALTH_RESPONSE" ]; then
        check_pass "Health endpoint responding"
    fi

    # Test API docs
    if curl -s "$API_BASE/docs" > /dev/null 2>&1; then
        check_pass "API documentation available at $API_BASE/docs"
    fi
else
    check_fail "Server is not running!"
    echo -e "${YELLOW}     Run: ./demo_quickstart.sh to start the server${NC}"
fi

# ==============================================================================
# CHECK 6: Demo Endpoints
# ==============================================================================

print_header "6️⃣  Demo Endpoints"

if curl -s "$API_BASE/" > /dev/null 2>&1; then
    # Test endpoint 1: Competitive response
    ENDPOINT1_TEST=$(curl -s -X POST "$API_BASE/generate-response-ad" \
        -H "Content-Type: application/json" \
        -d '{"competitor_ad_text": "Test ad"}' 2>&1)

    if echo "$ENDPOINT1_TEST" | grep -q "confidence_score"; then
        check_pass "/generate-response-ad endpoint working"
    else
        check_fail "/generate-response-ad endpoint failed"
    fi

    # Test endpoint 2: Opportunity campaign
    ENDPOINT2_TEST=$(curl -s -X POST "$API_BASE/generate_opportunity_campaign" \
        -H "Content-Type: application/json" \
        -d '{"city": "Test", "brand_rules": "Test"}' 2>&1)

    if echo "$ENDPOINT2_TEST" | grep -q "headline"; then
        check_pass "/generate_opportunity_campaign endpoint working"
    else
        check_fail "/generate_opportunity_campaign endpoint failed"
    fi
else
    check_warning "Cannot test endpoints - server not running"
fi

# ==============================================================================
# CHECK 7: Business Logic Tests
# ==============================================================================

print_header "7️⃣  Business Logic Tests"

if [ -f "test_business_logic.py" ]; then
    TEST_OUTPUT=$(python test_business_logic.py 2>&1)
    TEST_RESULT=$?

    if [ $TEST_RESULT -eq 0 ]; then
        PASSED=$(echo "$TEST_OUTPUT" | grep -o "[0-9]* passed" | awk '{print $1}')
        check_pass "All tests passing ($PASSED/10)"
    else
        FAILED=$(echo "$TEST_OUTPUT" | grep -o "[0-9]* failed" | awk '{print $1}')
        check_fail "Some tests failed ($FAILED failures)"
    fi
else
    check_fail "test_business_logic.py not found"
fi

# ==============================================================================
# CHECK 8: Demo Scripts
# ==============================================================================

print_header "8️⃣  Demo Scripts"

DEMO_SCRIPTS=("demo_quickstart.sh" "demo_execute.sh" "demo_healthcheck.sh")

for script in "${DEMO_SCRIPTS[@]}"; do
    if [ -f "$script" ]; then
        if [ -x "$script" ]; then
            check_pass "$script exists and is executable"
        else
            check_warning "$script exists but not executable (run: chmod +x $script)"
        fi
    else
        check_fail "$script not found"
    fi
done

# ==============================================================================
# FINAL REPORT
# ==============================================================================

echo ""
echo -e "${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [ $FAIL_COUNT -eq 0 ]; then
    cat << 'EOF'
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║                  ✅ ALL CHECKS PASSED - DEMO READY! ✅                     ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
EOF
    echo ""
    echo -e "${GREEN}🎉 Your demo environment is 100% ready!${NC}"
    echo ""
    echo -e "${CYAN}Next steps:${NC}"
    echo "  1. Keep server running (or start with: ./demo_quickstart.sh)"
    echo "  2. Open new terminal for demo execution: ./demo_execute.sh"
    echo "  3. Review talking points: cat DEMO_SCRIPT.md"
    echo "  4. Set 3-minute timer when presenting"
    echo ""
    echo -e "${BOLD}Good luck! 🚀${NC}"
else
    cat << 'EOF'
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║                 ⚠️  SOME ISSUES DETECTED - REVIEW ABOVE ⚠️                ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
EOF
    echo ""
    echo -e "${YELLOW}⚠️  Found $FAIL_COUNT issue(s) - please review above${NC}"
    echo ""
    echo -e "${CYAN}Quick fixes:${NC}"
    echo "  • Server not running? Run: ./demo_quickstart.sh"
    echo "  • Missing dependencies? Run: source .venv/bin/activate && uv pip install -r requirements.txt"
    echo "  • DEMO_MODE wrong? Run: echo 'DEMO_MODE=True' >> .env"
    echo "  • Scripts not executable? Run: chmod +x demo_*.sh"
    echo ""
fi

echo -e "${CYAN}Health Check Summary:${NC}"
echo -e "  ${GREEN}✅ Passed: $PASS_COUNT${NC}"
echo -e "  ${RED}❌ Failed: $FAIL_COUNT${NC}"
echo ""

# Exit with appropriate code
if [ $FAIL_COUNT -eq 0 ]; then
    exit 0
else
    exit 1
fi
