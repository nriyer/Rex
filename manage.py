# Main entry point for running different environments
import os
import sys

def run(env):
    os.environ['APP_SETTINGS'] = f'config.{env.capitalize()}'
    if env == 'dev':
        os.system('streamlit run app/main.py')
    elif env == 'staging':
        os.system('streamlit run app/main.py --server.port 8001')
    else:
        print("Invalid environment. Use: dev or staging.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python manage.py [dev|staging]")
    else:
        run(sys.argv[1])