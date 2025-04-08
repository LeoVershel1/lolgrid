#!/bin/bash

# Kill any existing Python processes running app.py
echo "Stopping any existing backend servers..."
pkill -f "python3 app.py" || true

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Start the backend server
echo "Starting backend server..."
cd "$(dirname "$0")"
PYTHONPATH="$PROJECT_ROOT" python3 app.py &
BACKEND_PID=$!

# Wait a moment for the backend to start
sleep 2

# Start the frontend server
echo "Starting frontend server..."
cd "$PROJECT_ROOT/frontend"
npm run dev &
FRONTEND_PID=$!

# Function to handle script termination
cleanup() {
  echo "Shutting down servers..."
  kill $BACKEND_PID 2>/dev/null || true
  kill $FRONTEND_PID 2>/dev/null || true
  exit 0
}

# Set up trap to catch termination signals
trap cleanup SIGINT SIGTERM

echo "Both servers are running!"
echo "Backend: http://localhost:5001"
echo "Frontend: http://localhost:3000"
echo "Press Ctrl+C to stop both servers"

# Keep the script running
wait 