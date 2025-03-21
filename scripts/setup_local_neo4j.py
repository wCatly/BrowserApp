#!/usr/bin/env python3
"""
Script to set up a local Neo4j Docker container for the Movie Search Engine.
This will create a Neo4j container with the correct configuration.
"""

import os
import sys
import subprocess
import time

# Default password for the Neo4j instance
DEFAULT_PASSWORD = "password"

def check_docker_installed():
    """Check if Docker is installed."""
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

def check_neo4j_container_exists():
    """Check if the Neo4j container already exists."""
    result = subprocess.run(
        ["docker", "ps", "-a", "--filter", "name=movie-neo4j", "--format", "{{.Names}}"],
        check=True, capture_output=True, text=True
    )
    return "movie-neo4j" in result.stdout

def start_neo4j_container(password=DEFAULT_PASSWORD):
    """Start the Neo4j container."""
    if check_neo4j_container_exists():
        print("Neo4j container already exists. Starting it...")
        subprocess.run(["docker", "start", "movie-neo4j"], check=True)
    else:
        print("Creating and starting a new Neo4j container...")
        # Create a Docker volume for persistent data
        subprocess.run(["docker", "volume", "create", "movie-neo4j-data"], check=True)
        
        # Start the Neo4j container
        cmd = [
            "docker", "run", "--name", "movie-neo4j",
            "-p", "7474:7474", "-p", "7687:7687",
            "-e", f"NEO4J_AUTH=neo4j/{password}",
            "-e", "NEO4J_ACCEPT_LICENSE_AGREEMENT=yes",
            "-v", "movie-neo4j-data:/data",
            "-d", "neo4j:4.4"
        ]
        subprocess.run(cmd, check=True)
    
    print("Waiting for Neo4j container to start up...")
    for _ in range(30):  # Wait up to 30 seconds
        time.sleep(1)
        try:
            health_cmd = ["docker", "exec", "movie-neo4j", "curl", "-s", "http://localhost:7474"]
            result = subprocess.run(health_cmd, capture_output=True)
            if result.returncode == 0:
                break
        except subprocess.SubprocessError:
            pass
    
    print("\nNeo4j container is now running!")
    print("You can access the Neo4j Browser at: http://localhost:7474")
    print(f"Username: neo4j")
    print(f"Password: {password}")

def update_config_file(password=DEFAULT_PASSWORD):
    """Update the config.py file with the correct password."""
    try:
        with open("config.py", "r") as f:
            config = f.read()
        
        # Update the password
        if "LOCAL_NEO4J_PASSWORD" in config:
            lines = config.splitlines()
            for i, line in enumerate(lines):
                if "LOCAL_NEO4J_PASSWORD" in line:
                    lines[i] = f'LOCAL_NEO4J_PASSWORD = "{password}"  # Change this to your local Neo4j password'
            
            # Set USE_LOCAL_NEO4J to True
            for i, line in enumerate(lines):
                if "USE_LOCAL_NEO4J" in line:
                    lines[i] = 'USE_LOCAL_NEO4J = True'
            
            with open("config.py", "w") as f:
                f.write("\n".join(lines))
            
            print("Updated config.py with the local Neo4j password.")
    except Exception as e:
        print(f"Error updating config.py: {e}")

def main():
    """Main function to set up Neo4j Docker container."""
    print("Movie Search Engine - Local Neo4j Setup")
    print("=======================================")
    
    if not check_docker_installed():
        print("Error: Docker is not installed or not in the PATH.")
        print("Please install Docker and try again.")
        return 1
    
    # Ask for password
    password = input(f"Enter Neo4j password (default: {DEFAULT_PASSWORD}): ").strip()
    if not password:
        password = DEFAULT_PASSWORD
    
    try:
        start_neo4j_container(password)
        update_config_file(password)
        print("\nSetup complete! You can now run the main application:")
        print("python main.py")
    except Exception as e:
        print(f"Error setting up Neo4j container: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 