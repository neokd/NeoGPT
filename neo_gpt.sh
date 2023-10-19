#!/bin/bash
  

# Set the default options
MODEL_DIR="gpt-3.5-turbo"
TEMP_DIR="/tmp/neo_gpt"
API_KEY="YOUR_OPENAI_API_KEY"

# Function to display usage instructions
usage() {
  echo "Usage: $0 [options] text"
  echo "Options:"
  echo "  -m, --model-dir DIR    Specify the model directory (default: gpt-3.5-turbo)"
  echo "  -o, --output FILE      Specify the output file (default: stdout)"
  echo "  -t, --temp-dir DIR     Specify the temporary directory (default: /tmp/neo_gpt)"
  echo "  -k, --api-key KEY      Specify your OpenAI API key (default: YOUR_OPENAI_API_KEY)"
  echo "  -h, --help             Show this help message"
  exit 1
}

# Parse command line options
while [[ $# -gt 0 ]]; do
  case "$1" in
    -m|--model-dir)
      MODEL_DIR="$2"
      shift 2
      ;;
    -o|--output)
      OUTPUT_FILE="$2"
      shift 2
      ;;
    -t|--temp-dir)
      TEMP_DIR="$2"
      shift 2
      ;;
    -k|--api-key)
      API_KEY="$2"
      shift 2
      ;;
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

# Check if required arguments are provided
if [ -z "$TEXT" ]; then
  echo "Error: Missing text input."
  usage
fi

# Create the temporary directory if it doesn't exist
mkdir -p "$TEMP_DIR"

# Run NeoGPT
if [ -z "$OUTPUT_FILE" ]; then
  openai api completions.create --model "$MODEL_DIR" --max_tokens 150 --temperature 0.7 --top_p 1.0 --stop "" --prompt "$TEXT" > "$TEMP_DIR/response.json"
  cat "$TEMP_DIR/response.json" | jq -r '.choices[0].text'
else
  openai api completions.create --model "$MODEL_DIR" --max_tokens 150 --temperature 0.7 --top_p 1.0 --stop "" --prompt "$TEXT" > "$OUTPUT_FILE"
fi

# To use the script, follow these steps:

# Save the script to a file, e.g., neo_gpt.sh.
# Make the script executable with the command: chmod +x neo_gpt.sh.
# Run NeoGPT with your desired text input and options. For example:

# ./neo_gpt.sh "Translate the following English text to French: 'Hello, world!'" -m "gpt-3.5-turbo" -o output.txt
