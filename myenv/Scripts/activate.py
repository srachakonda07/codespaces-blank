import subprocess

# Path to the activate script
activate_script = '/workspaces/codespaces-blank/myenv/Scripts/activate'

# Run the activate script
subprocess.run(['source', activate_script], shell=True)