#!/bin/bash

# Set your OpenAI API key
API_KEY="YOUR_OPENAI_API_KEY"

# Function to display usage instructions
usage() {
  echo "Usage: $0 [options] text"
  echo "Options:"
  echo "  -h, --help             Show this help message"
  exit 1
}

# Parse command line options
while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)
      usage
      ;;
    *)
      TEXT="$1"
      shift
      ;;
  esac
done

# Check if the OpenAI API key is set
if [ -z "$API_KEY" ] || [ "$API_KEY" == "YOUR_OPENAI_API_KEY" ]; then
  echo "Please set your OpenAI API key by editing this script."
  exit 1
fi

# Create a temporary directory for NeoGPT
NEOGPT_DIR="/tmp/neogpt"
mkdir -p "$NEOGPT_DIR"
cd "$NEOGPT_DIR"

# Clone the NeoGPT repository
git clone https://github.com/openai/gpt-3.5-turbo.git

# Change to the NeoGPT directory
cd gpt-3.5-turbo

# Install Python dependencies from requirements.txt
pip install -r requirements.txt

# Set the OpenAI API key
export OPENAI_API_KEY="$API_KEY"

# Run NeoGPT with the provided text
python main.py --text "$TEXT"

# Clean up: Remove the temporary directory
cd ..
rm -rf "$NEOGPT_DIR"

# To use the script, follow these steps:

# Save the script to a file, e.g., neo_gpt.sh.
# Make the script executable with the command: chmod +x neo_gpt.sh.
# Run NeoGPT with your desired text input and options. For example:

# ./neo_gpt.sh "Translate the following English text to French: 'Hello, world!'" -m "gpt-3.5-turbo" -o output.txt
