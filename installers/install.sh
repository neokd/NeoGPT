#!/bin/bash

# Colors for better presentation
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Display a welcome message
echo -e "Hello there! I'm NeoGPT, your virtual assistant for installation. Let's get started!"

# Ask the user if they want to proceed with the script
read -p "Would you like to continue with the NeoGPT installation? (y/n): " continue_installation

# Check the user's response
if [ "$continue_installation" == "y" ]; then
    # Display a friendly message
    echo -e "${GREEN}Great! I'm here to assist you.${NC}"

    os_type=$(uname -s)

    # Check if Python is installed based on OS type
    if [ "$os_type" == "Darwin" ] || [ "$os_type" == "Linux" ]; then
        if command -v python3 &>/dev/null; then
            python_cmd="python3"
            python_version=$($python_cmd -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
            echo -e "${GREEN}Found Python version $python_version.${NC}"
        else
            echo -e "${RED}Python is not installed. Please install Python version 3.10 or later.${NC}"
            exit 1
        fi
    elif [ "$os_type" == "Windows" ]; then
        if command -v python &>/dev/null; then
            python_cmd="python"
            python_version=$($python_cmd -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
            echo -e "${GREEN}Found Python version $python_version.${NC}"
        else
            echo -e "${RED}Python is not installed. Please install Python version 3.10 or later.${NC}"
            exit 1
        fi
    else
        echo -e "${RED}Unsupported operating system.${NC}"
        exit 1
    fi

    # Add your installation steps here

    # Example: Cloning a repository
    echo -e "${YELLOW}Cloning the NeoGPT repository...${NC}"
    git clone https://github.com/neokd/NeoGPT.git
    cd NeoGPT

    # Display a menu for installation options
    while true; do
        echo -e "How would you like to install dependencies?"
        echo -e "1. Using pip"
        echo -e "2. Using conda"
        read -p "Enter the number of your choice (1/2): " install_choice

        # Add installation steps based on user's choice
        case $install_choice in
            1)
                echo -e "${YELLOW}Installing dependencies using pip...${NC}"
                # Check if pip installed
                if pip &>/dev/null; then
                    # Create a virtual environment
                    python -m venv neogpt-venv
                    # Activate the virtual environment
                    source neogpt-venv/bin/activate
                    # Install dependencies using pip
                    pip install -e .
                else
                    echo -e "${RED}venv module is not available. Please install Python with venv support.${NC}"
                    pip install virtualenv
                    continue
                fi
                ;;
            2)
                echo -e "${YELLOW}Installing dependencies using conda...${NC}"
                # Check if conda is installed
                if command -v conda &>/dev/null; then
                    conda create --name neogpt-env python=3.10
                    conda activate neogpt-env
                    pip install -e .
                else
                    echo -e "${RED}conda is not installed. Please install conda to proceed.${NC}"
                    continue
                fi
                ;;
            *)
                echo -e "${RED}Invalid choice. Please select a valid option.${NC}"
                continue
                ;;
        esac
        # If the installation is successful, break out of the loop
        break
    done

    # Display a completion message
    echo -e "${GREEN}Installation completed successfully!${NC}"

    echo -e "${NC}Run the following command to start NeoGPT:${NC}"
    echo -e "${YELLOW}python main.py --build${NC}"
    echo -e "${NC} Refer docs at https://neokd.github.io/NeoGPT/ for more details.${NC}"


else
    echo -e "${YELLOW}Alright! If you change your mind, I'm here to help.${NC}"
fi
