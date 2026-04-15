#!/usr/bin/env bash
set -euo pipefail

scibudy collect "simulation-based calibration" --target-dir ~/Desktop/sbc-library
scibudy libraries
scibudy ingest-library "$1"
scibudy analyze-topic "$1" calibration
