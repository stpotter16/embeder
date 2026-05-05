#!/usr/bin/env bash
set -euo pipefail

echo "Deploying embeder to Fly.io..."
fly deploy
echo "Done. Check status with: fly status"
