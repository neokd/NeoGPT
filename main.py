import sys

from neogpt.cli import main


def find_main_modules():
    """
    Find names of main modules that are always loaded.
    """
    main_modules = set()

    for module_name, module in sys.modules.items():
        # Check if the module is a main module
        if hasattr(module, "__file__") and module.__file__:
            # Exclude modules from site-packages, they are usually not main modules
            if "site-packages" not in module.__file__:
                main_modules.add(module_name)

    return main_modules


if __name__ == "__main__":
    # Parse the arguments
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting NeoGPT 🤖")
        sys.exit()
