#!/bin/bash
# =================================================================
# CRIP Enterprise Platform - Performance Test Runner (Bash)
# =================================================================
#
# This script starts the Locust performance test against the platform.
#
# USAGE:
#   ./scripts/run_perf_test.sh
#
# It will:
# 1. Check if Docker services are running.
# 2. Run the Locust test.
# 3. Provide a link to the web UI.
#
# =================================================================

# --- Configuration ---
LOCUST_FILE="scripts/locustfile.py"
LOCUST_WEB_UI_PORT="8089"
PROJECT_DIR=$(dirname "$0")/..

# --- Functions ---
check_docker_services() {
    echo "🔍 Checking if platform services are running..."
    RUNNING_SERVICES=$(docker-compose ps --services --filter "status=running" | wc -l)
    # Expecting at least 7 services (gateway + 6 core services)
    if [ "$RUNNING_SERVICES" -lt 7 ]; then
        echo "⚠️ Not all services are running."
        read -p "Do you want to start them now? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "🚀 Starting services with 'docker-compose up -d'..."
            docker-compose up -d
            echo "⏳ Waiting 15 seconds for services to initialize..."
            sleep 15
        else
            echo "❌ Aborting. Please start services manually with 'docker-compose up -d'."
            exit 1
        fi
    fi
    echo "✅ All services appear to be running."
}

# --- Main Script ---
echo -e "\033[0;32m🚀 Starting CRIP Performance Test...\033[0m"
cd "$PROJECT_DIR" || exit

check_docker_services

echo -e "\033[0;32m📈 Launching Locust...\033[0m"
echo -e "   Open your browser and navigate to: \033[0;36mhttp://localhost:$LOCUST_WEB_UI_PORT\033[0m"
echo "   Press CTRL+C in this terminal to stop the test."

locust -f $LOCUST_FILE