#!/bin/bash
# Screen-U Quick Start Script

echo "🚀 Starting Screen-U Backend & Frontend..."
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Start Backend
echo -e "${BLUE}[1/2] Starting Flask Backend...${NC}"
cd backend
python app.py &
BACKEND_PID=$!
sleep 3

# Check if backend started
if curl -s http://localhost:5000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend running on http://localhost:5000${NC}"
else
    echo "❌ Backend failed to start. Check .env file and try again."
    exit 1
fi

# Start Frontend
echo ""
echo -e "${BLUE}[2/2] Starting React Frontend...${NC}"
cd ../frontend
npm run dev &
FRONTEND_PID=$!
sleep 5

echo ""
echo -e "${GREEN}✅ Both servers running!${NC}"
echo ""
echo "Frontend:  http://localhost:5173"
echo "Backend:   http://localhost:5000"
echo ""
echo "Open http://localhost:5173 in your browser to start screening! 🎉"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for both processes
wait
