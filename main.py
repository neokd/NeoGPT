from neogpt.cli import main
import sys

if __name__ == "__main__":
    # Parse the arguments
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting NeoGPT 🤖")
        sys.exit()
