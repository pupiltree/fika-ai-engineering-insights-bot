#!/usr/bin/env python3
import sys
import subprocess
import os

def run_command(cmd):
    """Run a shell command."""
    return subprocess.run(cmd, shell=True, check=True)

def install():
    """Install dependencies."""
    print("📦 Installing dependencies...")
    run_command("pip install -r requirements.txt")

def setup():
    """Setup project."""
    print("🔧 Setting up project...")
    install()
    run_command("python scripts/setup_db.py")

def seed():
    """Seed database."""
    print("🌱 Seeding database...")
    run_command("python scripts/seed_data.py")

def run_server():
    """Start server."""
    print("🚀 Starting server...")
    run_command("python scripts/run_local.py")

def clean():
    """Clean up."""
    print("🧹 Cleaning up...")
    files_to_remove = [
        "data/productivity.db",
        "__pycache__",
        "src/__pycache__"
    ]
    for file in files_to_remove:
        if os.path.exists(file):
            if os.path.isdir(file):
                import shutil
                shutil.rmtree(file)
            else:
                os.remove(file)

def show_help():
    """Show help."""
    print("""
Engineering Productivity MVP Commands:

  python manage.py setup    - Install dependencies and set up database
  python manage.py run      - Start the development server  
  python manage.py seed     - Populate database with sample data
  python manage.py install  - Install dependencies only
  python manage.py clean    - Clean up generated files

Quick start:
  1. Copy .env.example to .env and fill in your API keys
  2. python manage.py setup
  3. python manage.py seed
  4. python manage.py run
""")

if __name__ == "__main__":
    commands = {
        "install": install,
        "setup": setup,
        "seed": seed,
        "run": run_server,
        "clean": clean,
        "help": show_help
    }
    
    if len(sys.argv) < 2:
        show_help()
    else:
        cmd = sys.argv[1].lower()
        if cmd in commands:
            commands[cmd]()
        else:
            print(f"Unknown command: {cmd}")
            show_help()