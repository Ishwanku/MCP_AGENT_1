import multiprocessing
import sys
from pathlib import Path

def run_server(module_name):
    """Run a server module using Python's -m flag."""
    try:
        import importlib
        module = importlib.import_module(module_name)
        if hasattr(module, 'run'):
            module.run()
    except Exception as e:
        print(f"Error starting {module_name}: {str(e)}")

def main():
    # List of all server modules to start
    servers = [
        'src.mcp.agents.tasks_agent',
        'src.mcp.agents.calendar_agent',
        'src.mcp.agents.memory_agent',
        'src.mcp.agents.crawler_agent'
    ]
    
    # Create a process for each server
    processes = []
    for server in servers:
        process = multiprocessing.Process(target=run_server, args=(server,))
        processes.append(process)
        process.start()
        print(f"Started {server}")
    
    # Wait for all processes to complete
    try:
        for process in processes:
            process.join()
    except KeyboardInterrupt:
        print("\nShutting down all servers...")
        for process in processes:
            process.terminate()
        sys.exit(0)

if __name__ == '__main__':
    # Ensure we're running from the project root
    project_root = Path(__file__).parent
    sys.path.append(str(project_root))
    
    # Set multiprocessing start method
    multiprocessing.set_start_method('spawn')
    
    print("Starting all MCP servers...")
    main() 