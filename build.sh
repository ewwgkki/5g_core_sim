#!/usr/bin/env bash
# build.sh — Build 5G Core Sim into a standalone distribution
# Usage: ./build.sh           (foreground, see output directly)
#        ./build.sh --bg      (background, survives session disconnect)
# Output: dist/5g_core_sim/ (ready to deploy)
# Log:    build.log (when running in background)

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Background mode: re-launch self with nohup
if [ "$1" = "--bg" ]; then
    echo "Starting build in background..."
    echo "Log: $SCRIPT_DIR/build.log"
    echo "Check progress: tail -f build.log"
    nohup bash "$0" > build.log 2>&1 &
    echo "Build PID: $!"
    exit 0
fi

echo "=== 5G Core Sim — Build Script ==="
echo ""

# ── 1. Check dependencies ────────────────────────────
echo "[1/5] Checking build dependencies..."
if ! command -v python3 &>/dev/null; then
    echo "ERROR: python3 not found"
    exit 1
fi

PYTHON_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "  Python: $PYTHON_VER"

# Create virtual environment for build
VENV_DIR="$SCRIPT_DIR/.build_venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "  Creating build virtual environment..."
    python3 -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"
pip install --quiet --upgrade pip 2>/dev/null || true

# Install from local build_wheels/ if available (offline), else from PyPI
WHEELS_DIR="$SCRIPT_DIR/build_wheels"
if [ -d "$WHEELS_DIR" ] && [ "$(ls -A $WHEELS_DIR/*.whl 2>/dev/null)" ]; then
    echo "  Installing from local build_wheels/ (offline)..."
    pip install --quiet --no-index --find-links "$WHEELS_DIR" pyinstaller
else
    echo "  Installing from PyPI (online)..."
    pip install --quiet pyinstaller
fi
echo "  PyInstaller: $(python -m PyInstaller --version 2>/dev/null || echo 'installed')"

# ── 2. Install project dependencies ──────────────────
echo ""
echo "[2/5] Installing project dependencies..."
if [ -d "$WHEELS_DIR" ] && [ "$(ls -A $WHEELS_DIR/*.whl 2>/dev/null)" ]; then
    pip install --quiet --no-index --find-links "$WHEELS_DIR" -r requirements-modern.txt
else
    pip install --quiet -r requirements-modern.txt
fi

# ── 3. Run PyInstaller ────────────────────────────────
echo ""
echo "[3/5] Building with PyInstaller..."

# Clean previous build
rm -rf build/ dist/5g_core_sim/

python3 -m PyInstaller \
    --noconfirm \
    --clean \
    --name 5g_core_sim \
    --distpath dist \
    --specpath build \
    --hidden-import=uvicorn \
    --hidden-import=hypercorn \
    --hidden-import=hypercorn.asyncio \
    --hidden-import=hypercorn.config \
    --hidden-import=fastapi \
    --hidden-import=starlette \
    --hidden-import=starlette.routing \
    --hidden-import=starlette.middleware \
    --hidden-import=starlette.middleware.errors \
    --hidden-import=starlette.exceptions \
    --hidden-import=starlette.responses \
    --hidden-import=starlette.staticfiles \
    --hidden-import=starlette.concurrency \
    --hidden-import=pydantic \
    --hidden-import=httpx \
    --hidden-import=httpcore \
    --hidden-import=h2 \
    --hidden-import=hpack \
    --hidden-import=hyperframe \
    --hidden-import=h11 \
    --hidden-import=aiofiles \
    --hidden-import=anyio \
    --hidden-import=sniffio \
    --hidden-import=nrf \
    --hidden-import=nrf.main \
    --hidden-import=nrf.config \
    --hidden-import=nrf.models \
    --hidden-import=amf \
    --hidden-import=amf.main \
    --hidden-import=amf.config \
    --hidden-import=amf.api \
    --hidden-import=amf.api.namf_loc \
    --hidden-import=amf.api.namf_comm \
    --hidden-import=amf.session \
    --hidden-import=udm \
    --hidden-import=udm.main \
    --hidden-import=udm.config \
    --hidden-import=udm.api \
    --hidden-import=udm.api.uecm \
    --hidden-import=udm.api.ueau \
    --hidden-import=udm.api.sdm \
    --hidden-import=web \
    --hidden-import=web.main \
    --hidden-import=web.config_store \
    --hidden-import=utils \
    --hidden-import=utils.serve \
    --hidden-import=utils.path \
    --hidden-import=utils.bootstrap \
    --collect-submodules=starlette \
    --collect-submodules=fastapi \
    run_web.py

echo "  Binary built: dist/5g_core_sim/"

# ── 4. Copy runtime files ─────────────────────────────
echo ""
echo "[4/5] Copying runtime files..."

DIST="dist/5g_core_sim"

# Web GUI static files
mkdir -p "$DIST/web/static"
cp web/static/index.html "$DIST/web/static/"

# Additional entry scripts (packaged as data, launched by main binary)
cp run_nrf.py run_amf.py run_udm.py run_web.py "$DIST/"

# Source modules (needed because services are spawned as subprocesses)
cp -r nrf/ "$DIST/nrf/"
cp -r amf/ "$DIST/amf/"
cp -r udm/ "$DIST/udm/"
cp -r web/ "$DIST/web_src/"
cp -r utils/ "$DIST/utils/"

# Config template
cp config.json "$DIST/config.json"

# Remove __pycache__
find "$DIST" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find "$DIST" -name "*.pyc" -delete 2>/dev/null || true
find "$DIST" -name ".DS_Store" -delete 2>/dev/null || true

# ── 5. Create launcher scripts ────────────────────────
echo ""
echo "[5/5] Creating launcher scripts..."

# Main web console launcher
cat > "$DIST/start.sh" << 'EOF'
#!/usr/bin/env bash
# Start 5G Core Sim Web Console (manages all services)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"
echo "Starting 5G Core Sim Web Console..."
echo "Open http://127.0.0.1:8080 in your browser"
./5g_core_sim &
echo "PID: $!"
echo "To stop: kill $!"
EOF
chmod +x "$DIST/start.sh"

# Individual service launchers
cat > "$DIST/start_nrf.sh" << 'EOF'
#!/usr/bin/env bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"
HOST=${1:-127.0.0.1}
PORT=${2:-8000}
echo "Starting NRF on $HOST:$PORT ..."
python3 run_nrf.py "$HOST" "$PORT" &
echo "NRF PID: $!"
EOF
chmod +x "$DIST/start_nrf.sh"

cat > "$DIST/start_amf.sh" << 'EOF'
#!/usr/bin/env bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"
HOST=${1:-127.0.0.1}
PORT=${2:-9999}
echo "Starting AMF on $HOST:$PORT ..."
python3 run_amf.py "$HOST" "$PORT" &
echo "AMF PID: $!"
EOF
chmod +x "$DIST/start_amf.sh"

cat > "$DIST/start_udm.sh" << 'EOF'
#!/usr/bin/env bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"
HOST=${1:-127.0.0.1}
PORT=${2:-5555}
echo "Starting UDM on $HOST:$PORT ..."
python3 run_udm.py "$HOST" "$PORT" &
echo "UDM PID: $!"
EOF
chmod +x "$DIST/start_udm.sh"

cat > "$DIST/start_all.sh" << 'EOF'
#!/usr/bin/env bash
# Start all services individually (no Web Console)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"
echo "Starting all 5G Core services..."
bash start_nrf.sh
sleep 2
bash start_amf.sh
bash start_udm.sh
echo ""
echo "All services started. Config: config.json"
echo "To stop all: ./stop.sh"
EOF
chmod +x "$DIST/start_all.sh"

cat > "$DIST/stop.sh" << 'EOF'
#!/usr/bin/env bash
# Stop all 5G Core Sim processes
echo "Stopping 5G Core Sim..."
pkill -f "5g_core_sim" 2>/dev/null
pkill -f "run_nrf.py" 2>/dev/null
pkill -f "run_amf.py" 2>/dev/null
pkill -f "run_udm.py" 2>/dev/null
pkill -f "run_web.py" 2>/dev/null
echo "Done."
EOF
chmod +x "$DIST/stop.sh"

# ── Done ──────────────────────────────────────────────
echo ""
echo "=== Build complete! ==="
echo ""
echo "Output: dist/5g_core_sim/"
echo ""
echo "To deploy:"
echo "  1. Copy dist/5g_core_sim/ to target machine"
echo "  2. Edit config.json as needed"
echo ""
echo "Start options:"
echo "  ./start.sh           — Web Console (GUI manages all services)"
echo "  ./start_all.sh       — Start NRF + AMF + UDM without Web Console"
echo "  ./start_nrf.sh       — Start NRF only"
echo "  ./start_amf.sh       — Start AMF only"
echo "  ./start_udm.sh       — Start UDM only"
echo "  ./stop.sh            — Stop everything"
echo ""
echo "Optional args: ./start_nrf.sh [host] [port]"
echo ""
echo "Contents:"
du -sh "$DIST"
echo ""
ls "$DIST"/*.sh "$DIST/config.json" 2>/dev/null

# Deactivate build venv
deactivate 2>/dev/null || true
