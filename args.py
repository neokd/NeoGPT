import argparse
import psutil

def get_cpu_info():
    cpu_info = {}
    cpu_info['CPU'] = psutil.cpu_info()[0].model
    cpu_info['Cores'] = psutil.cpu_count(logical=False)
    cpu_info['Threads'] = psutil.cpu_count(logical=True)
    cpu_info['Usage'] = psutil.cpu_percent(interval=1)

    return cpu_info

def get_gpu_info():
    
    try:
        import gpustat
        gpu_info = gpustat.GPUStatCollection.new_query().jsonify()
    except ImportError:
        gpu_info = "gpustat library not installed. Install it for better GPU information."

    return gpu_info

def main():
    parser = argparse.ArgumentParser(description="Get CPU and GPU Information")

    parser.add_argument(
        "--device_type",
        choices=["cpu", "gpu"],
        default="cpu",
        help="Specify the device type (cpu, gpu)",
    )
    parser.add_argument(
        "--specific_model",
        type=str,
        default="default",
        help="Specify the specific model or identifier",
    )

    args = parser.parse_args()

    if args.device_type == "cpu":
        info = get_cpu_info()
    elif args.device_type == "gpu":
        info = get_gpu_info()
    else:
        info = "Invalid device type specified."

    print(f"Device Type: {args.device_type}")
    print(f"Specific Model: {args.specific_model}")
    print(info)

if __name__ == "__main__":
    main()
