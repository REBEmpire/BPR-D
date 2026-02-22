import sys
import os
import importlib.util

# Shim to load the actual app from crewai-service/main.py
# We cannot use 'import main' because that would refer to THIS file (circular import).

current_dir = os.path.dirname(os.path.abspath(__file__))
service_dir = os.path.join(current_dir, 'crewai-service')

# Add crewai-service to sys.path so dependencies inside it (like agents, config) can be imported
if service_dir not in sys.path:
    sys.path.insert(0, service_dir)

# Manually load the module from the specific path with a unique name
target_path = os.path.join(service_dir, 'main.py')
spec = importlib.util.spec_from_file_location("crewai_service_main", target_path)
crewai_service_main = importlib.util.module_from_spec(spec)
sys.modules["crewai_service_main"] = crewai_service_main
spec.loader.exec_module(crewai_service_main)

# Expose the app object for uvicorn
app = crewai_service_main.app

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
