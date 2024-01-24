

# Needed Imports 
import platform
import importlib.metadata
import psutil





def get_python_version() -> str:
    """
    Retrieves the current Python version in use.

    Returns:
        str: The Python version as a string.
    """
    return platform.python_version()


def get_os_version() -> str:
    """
    Fetches the operating system's name, version, and other relevant details using the 'platform' module. 

    Returns:
        str:  gives informative description of the operating system, such as 'Windows-10-10.0.19041-SP0' or 'Linux-5.4.0-42-generic-x86_64-with-Ubuntu-20.04-focal'.
    """
    return platform.platform()



def get_ram_info() -> str:
    """
    Retrieves detailed information about the system's RAM, including total, used, free, and available memory.

    Returns:
        str: A formatted string displaying detailed RAM information.
    """
    ram = psutil.virtual_memory()
    total_ram_gb = ram.total / 2**30
    available_ram_gb = ram.available / 2**30
    used_ram_gb = (ram.total - ram.available) / 2**30
    free_ram_gb = ram.free / 2**30
    used_ram_percentage = (used_ram_gb / total_ram_gb) * 100

    return (f"RAM Details:\n"
            f"  Total RAM: {total_ram_gb:.2f} GB\n"
            f"  Used RAM: {used_ram_gb:.2f} GB ({used_ram_percentage:.2f}%)\n"
            f"  Free RAM: {free_ram_gb:.2f} GB\n"
            f"  Available RAM: {available_ram_gb:.2f} GB\n"
            f"  (Note: 'Available' RAM includes memory that is currently in use but can be released for new applications.)")





def get_cpu_info() -> str:
   
    """
    Provides a summary of CPU performance, including overall and per-core utilization, core counts, and frequency ranges.

    Returns:
        str: A compact overview of CPU metrics, highlighting total and core-specific usage, core counts, and frequency stats.
    """
    # Overall CPU usage
    cpu_usage_total = psutil.cpu_percent(interval=1)
    
    # Per-core CPU usage
    cpu_usage_per_core = psutil.cpu_percent(interval=1, percpu=True)
    cpu_cores_usage_str = ', '.join([f"{usage}%" for usage in cpu_usage_per_core])
    
    # Number of logical and physical cores
    logical_cores = psutil.cpu_count()
    physical_cores = psutil.cpu_count(logical=False)
    
    # CPU frequency
    cpu_freq = psutil.cpu_freq()
    if cpu_freq:
        current_freq, min_freq, max_freq = cpu_freq.current, cpu_freq.min, cpu_freq.max
    else:
        current_freq, min_freq, max_freq = ('N/A', 'N/A', 'N/A')

    return (f"CPU Information:\n"
            f"  Total Usage: {cpu_usage_total}% - This represents the overall CPU workload as a percentage of its total capacity.\n"
            f"  Per-Core Usage: {cpu_cores_usage_str} - These values show the workload distribution across each CPU core.\n"
            f"  Logical Cores: {logical_cores} - The total number of logical CPU cores available, including hyper-threaded cores.\n"
            f"  Physical Cores: {physical_cores if physical_cores else 'N/A'} - The number of actual physical CPU cores, excluding hyper-threading.\n"
            f"  Frequency (MHz): Current: {current_freq}, Min: {min_freq}, Max: {max_freq} - The CPU's operating frequency range, with the current frequency indicating its current operating speed.")







def get_neogpt_version() -> str:
    """
    Retrieves the NeoGPT library version installed in the environment.

    Returns:
        str: The NeoGPT library version, e.g., '1.0.3'. Raises a RuntimeError if the package is not found.
    """
    try:
        return importlib.metadata.version('neogpt')
    except importlib.metadata.PackageNotFoundError:
        raise RuntimeError("NeoGPT package is not installed.")
    



# def neogpt_info() to display current version of neogpt, model used, max_tokens, 