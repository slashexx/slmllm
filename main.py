import uvicorn
import yaml
import sys


def main():
    try:
        with open("config.yaml", 'r') as f:
            config = yaml.safe_load(f)
        
        host = config['server']['host']
        port = config['server']['port']
        
        print(f"Starting LLM-SLM Router API on {host}:{port}")
        uvicorn.run("api:app", host=host, port=port, reload=True)
    except FileNotFoundError:
        print("Error: config.yaml not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting server: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

