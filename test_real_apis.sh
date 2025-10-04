#!/bin/bash
# ==============================================================================
# REAL API INTEGRATION TEST
# ==============================================================================
# Tests all 5 sponsor APIs with REAL calls (no mocks)
# ==============================================================================

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

echo ""
echo -e "${BOLD}${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${CYAN}║                                                                ║${NC}"
echo -e "${BOLD}${CYAN}║         🔥 REAL API INTEGRATION TEST - NO MOCKS 🔥            ║${NC}"
echo -e "${BOLD}${CYAN}║                                                                ║${NC}"
echo -e "${BOLD}${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Verify DEMO_MODE=True (but using real APIs)
DEMO_MODE=$(grep -E "^DEMO_MODE=" .env | cut -d '=' -f2)
echo -e "${CYAN}DEMO_MODE:${NC} $DEMO_MODE ${YELLOW}(must use REAL APIs, not mocks!)${NC}"
echo ""

# Wait for user confirmation
echo -e "${YELLOW}This will make REAL API calls using your actual API keys.${NC}"
echo -e "${YELLOW}Press ENTER to continue, or Ctrl+C to cancel...${NC}"
read -r

echo ""
echo -e "${BOLD}Starting server in background...${NC}"

# Kill any existing server
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Start server in background
uvicorn main:app --host 0.0.0.0 --port 8000 > /tmp/server.log 2>&1 &
SERVER_PID=$!

echo -e "${GREEN}✓${NC} Server PID: $SERVER_PID"

# Wait for server to start
sleep 3

# Health check
echo ""
echo -e "${BOLD}Testing health endpoint...${NC}"
if curl -s http://localhost:8000/ > /dev/null; then
    echo -e "${GREEN}✓${NC} Server is responding"
else
    echo -e "${RED}✗${NC} Server failed to start!"
    kill $SERVER_PID 2>/dev/null || true
    exit 1
fi

# ==============================================================================
# TEST 1: Competitive Ad Generation (TrueFoundry + Freepik + DeepL + Datadog + ClickHouse)
# ==============================================================================

echo ""
echo -e "${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}TEST 1: Competitive Ad Generation${NC}"
echo -e "${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${YELLOW}Making REAL API call to /generate-response-ad...${NC}"
echo ""

RESPONSE=$(curl -s -X POST http://localhost:8000/generate-response-ad \
  -H "Content-Type: application/json" \
  -d '{
    "competitor_ad_text": "Red Bull gives you wings! Energy that lasts all day."
  }')

echo -e "${CYAN}API Response:${NC}"
echo "$RESPONSE" | jq '.' 2>/dev/null || echo "$RESPONSE"

# Check for real vs mock indicators
if echo "$RESPONSE" | grep -q "confidence_score"; then
    echo ""
    echo -e "${GREEN}✓${NC} Received JSON response with confidence_score"
else
    echo ""
    echo -e "${RED}✗${NC} Invalid response format"
fi

# Wait a bit for logs
sleep 2

# Check server logs for REAL API indicators
echo ""
echo -e "${BOLD}Checking server logs for REAL API calls...${NC}"
echo ""

if grep -q "🚀 REAL AD GENERATION - Using LIVE APIs" /tmp/server.log; then
    echo -e "${GREEN}✓${NC} REAL AD GENERATION mode detected"
else
    echo -e "${RED}✗${NC} Still using MOCK mode!"
fi

if grep -q "✅ TrueFoundry Response:" /tmp/server.log; then
    echo -e "${GREEN}✓${NC} TrueFoundry API called successfully"
else
    echo -e "${RED}✗${NC} TrueFoundry API not called"
fi

if grep -q "✅ Freepik" /tmp/server.log; then
    echo -e "${GREEN}✓${NC} Freepik API called"
else
    echo -e "${YELLOW}⚠${NC}  Freepik API not called (may have failed)"
fi

if grep -q "✅ DeepL Translation" /tmp/server.log; then
    echo -e "${GREEN}✓${NC} DeepL API called successfully"
else
    echo -e "${YELLOW}⚠${NC}  DeepL API not called (may be disabled)"
fi

if grep -q "✅ ClickHouse: Logged ad generation" /tmp/server.log; then
    echo -e "${GREEN}✓${NC} ClickHouse REAL logging"
else
    echo -e "${YELLOW}⚠${NC}  ClickHouse logging not detected"
fi

if grep -q "✅ Datadog: Sent metric" /tmp/server.log; then
    echo -e "${GREEN}✓${NC} Datadog REAL metrics sent"
else
    echo -e "${YELLOW}⚠${NC}  Datadog metrics not sent"
fi

# Check for MOCK indicators (should NOT be present!)
if grep -q "MOCK ANALYTICS LOG" /tmp/server.log; then
    echo -e "${RED}✗✗✗ MOCK ANALYTICS DETECTED - THIS IS WRONG!${NC}"
fi

if grep -q "DATADOG METRIC (MOCKED)" /tmp/server.log; then
    echo -e "${RED}✗✗✗ MOCKED DATADOG METRICS DETECTED - THIS IS WRONG!${NC}"
fi

# ==============================================================================
# TEST 2: Opportunity Campaign (Linkup + TrueFoundry + Freepik + ClickHouse + Datadog)
# ==============================================================================

echo ""
echo -e "${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}TEST 2: Opportunity Campaign Generation${NC}"
echo -e "${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${YELLOW}Making REAL API call to /generate_opportunity_campaign...${NC}"
echo ""

RESPONSE2=$(curl -s -X POST http://localhost:8000/generate_opportunity_campaign \
  -H "Content-Type: application/json" \
  -d '{
    "city": "Austin",
    "brand_rules": "Premium cold brew, sustainability-focused, young professionals"
  }')

echo -e "${CYAN}API Response:${NC}"
echo "$RESPONSE2" | jq '.' 2>/dev/null || echo "$RESPONSE2"

# Wait for logs
sleep 2

echo ""
echo -e "${BOLD}Checking server logs for REAL API calls...${NC}"
echo ""

if grep -q "🚀 REAL OPPORTUNITY CAMPAIGN - Using LIVE APIs" /tmp/server.log; then
    echo -e "${GREEN}✓${NC} REAL OPPORTUNITY CAMPAIGN mode detected"
else
    echo -e "${RED}✗${NC} Still using MOCK mode!"
fi

if grep -q "✅ Linkup: Opportunity Found" /tmp/server.log; then
    echo -e "${GREEN}✓${NC} Linkup API called successfully"
else
    echo -e "${RED}✗${NC} Linkup API not called"
fi

if grep -q "✅ TrueFoundry: Campaign Generated" /tmp/server.log; then
    echo -e "${GREEN}✓${NC} TrueFoundry API called successfully"
else
    echo -e "${RED}✗${NC} TrueFoundry API not called"
fi

if grep -q "✅ Freepik: Image Generated" /tmp/server.log; then
    echo -e "${GREEN}✓${NC} Freepik API called successfully"
else
    echo -e "${YELLOW}⚠${NC}  Freepik API not called"
fi

if grep -q "✅ ClickHouse: Logged campaign search" /tmp/server.log; then
    echo -e "${GREEN}✓${NC} ClickHouse REAL campaign logging"
else
    echo -e "${YELLOW}⚠${NC}  ClickHouse campaign logging not detected"
fi

# ==============================================================================
# SUMMARY
# ==============================================================================

echo ""
echo -e "${BOLD}${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${CYAN}║                                                                ║${NC}"
echo -e "${BOLD}${CYAN}║                  📊 TEST SUMMARY 📊                           ║${NC}"
echo -e "${BOLD}${CYAN}║                                                                ║${NC}"
echo -e "${BOLD}${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${BOLD}API Integration Status:${NC}"
echo ""

# Count successes
SUCCESS_COUNT=0
TOTAL_COUNT=5

if grep -q "✅ TrueFoundry" /tmp/server.log; then
    echo -e "  ${GREEN}✓${NC} TrueFoundry (GPT-5) - REAL API calls"
    ((SUCCESS_COUNT++))
else
    echo -e "  ${RED}✗${NC} TrueFoundry (GPT-5) - FAILED"
fi

if grep -q "✅ Linkup" /tmp/server.log; then
    echo -e "  ${GREEN}✓${NC} Linkup - REAL web search"
    ((SUCCESS_COUNT++))
else
    echo -e "  ${RED}✗${NC} Linkup - FAILED"
fi

if grep -q "✅ Freepik" /tmp/server.log; then
    echo -e "  ${GREEN}✓${NC} Freepik - REAL image generation"
    ((SUCCESS_COUNT++))
else
    echo -e "  ${YELLOW}⚠${NC}  Freepik - WARNING (may have failed)"
fi

if grep -q "✅ DeepL" /tmp/server.log; then
    echo -e "  ${GREEN}✓${NC} DeepL - REAL translation"
    ((SUCCESS_COUNT++))
else
    echo -e "  ${YELLOW}⚠${NC}  DeepL - Not tested (check API key)"
fi

if grep -q "✅ ClickHouse" /tmp/server.log; then
    echo -e "  ${GREEN}✓${NC} ClickHouse - REAL analytics logging"
    ((SUCCESS_COUNT++))
else
    echo -e "  ${YELLOW}⚠${NC}  ClickHouse - WARNING (may not be running)"
fi

if grep -q "✅ Datadog" /tmp/server.log; then
    echo -e "  ${GREEN}✓${NC} Datadog - REAL metrics"
else
    echo -e "  ${YELLOW}⚠${NC}  Datadog - WARNING (check API key)"
fi

echo ""
echo -e "${BOLD}Mock Detection (should be NONE):${NC}"
echo ""

if grep -q "MOCK ANALYTICS LOG" /tmp/server.log || grep -q "DATADOG METRIC (MOCKED)" /tmp/server.log; then
    echo -e "  ${RED}✗✗✗ MOCKS DETECTED - URGENT FIX NEEDED!${NC}"
else
    echo -e "  ${GREEN}✓${NC} No mocks detected - all integrations are REAL!"
fi

echo ""
echo -e "${BOLD}Server Logs:${NC} /tmp/server.log"
echo -e "${BOLD}Server PID:${NC} $SERVER_PID"
echo ""

# Keep server running for demo
echo -e "${YELLOW}Server is still running for your demo.${NC}"
echo -e "${YELLOW}To stop it: kill $SERVER_PID${NC}"
echo ""

echo -e "${GREEN}✅ REAL API INTEGRATION TEST COMPLETE${NC}"
echo ""
