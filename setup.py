#!/usr/bin/env python3
"""
Python cross-platform setup script for Telegram Automation Bot
Run: python setup.py
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


class ProjectSetup:
    """Setup the Telegram Automation Bot project"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.venv_path = self.project_root / "venv"
        self.logs_dir = self.project_root / "logs"
        self.env_file = self.project_root / ".env"
        self.env_example = self.project_root / ".env.example"
    
    def print_header(self):
        """Print setup header"""
        print("\n" + "="*40)
        print("Telegram Automation Bot - Setup")
        print("="*40 + "\n")
    
    def print_success(self, message):
        """Print success message"""
        print(f"✓ {message}")
    
    def print_error(self, message):
        """Print error message"""
        print(f"✗ {message}")
        sys.exit(1)
    
    def print_info(self, message):
        """Print info message"""
        print(f"→ {message}")
    
    def check_python(self):
        """Check Python installation"""
        self.print_info("Checking Python installation...")
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            self.print_error(f"Python 3.8+ required, found {version.major}.{version.minor}")
        self.print_success(f"Python {version.major}.{version.minor}.{version.micro} found")
    
    def create_venv(self):
        """Create virtual environment"""
        self.print_info("Creating virtual environment...")
        if self.venv_path.exists():
            self.print_success("Virtual environment already exists")
            return
        
        try:
            subprocess.run([sys.executable, "-m", "venv", str(self.venv_path)], check=True)
            self.print_success("Virtual environment created")
        except subprocess.CalledProcessError:
            self.print_error("Failed to create virtual environment")
    
    def get_pip_executable(self):
        """Get pip executable path"""
        if os.name == "nt":  # Windows
            return self.venv_path / "Scripts" / "pip"
        else:  # Unix
            return self.venv_path / "bin" / "pip"
    
    def upgrade_pip(self):
        """Upgrade pip"""
        self.print_info("Upgrading pip...")
        pip_exe = self.get_pip_executable()
        try:
            subprocess.run([str(pip_exe), "install", "--upgrade", "pip"], check=True)
            self.print_success("pip upgraded")
        except subprocess.CalledProcessError:
            self.print_error("Failed to upgrade pip")
    
    def install_requirements(self):
        """Install requirements"""
        self.print_info("Installing dependencies...")
        requirements_file = self.project_root / "requirements.txt"
        if not requirements_file.exists():
            self.print_error("requirements.txt not found")
        
        pip_exe = self.get_pip_executable()
        try:
            subprocess.run([str(pip_exe), "install", "-r", str(requirements_file)], check=True)
            self.print_success("Dependencies installed")
        except subprocess.CalledProcessError:
            self.print_error("Failed to install dependencies")
    
    def setup_env_file(self):
        """Setup environment file"""
        self.print_info("Setting up environment configuration...")
        if self.env_file.exists():
            self.print_success(".env file already exists")
            return
        
        if self.env_example.exists():
            shutil.copy(str(self.env_example), str(self.env_file))
            self.print_success(".env file created from template")
            print("  ⚠ Please update .env with your credentials")
        else:
            self.print_error(".env.example not found")
    
    def create_logs_directory(self):
        """Create logs directory"""
        self.print_info("Setting up logs directory...")
        if self.logs_dir.exists():
            self.print_success("logs directory already exists")
            return
        
        try:
            self.logs_dir.mkdir(parents=True, exist_ok=True)
            self.print_success("logs directory created")
        except Exception as e:
            self.print_error(f"Failed to create logs directory: {e}")
    
    def print_next_steps(self):
        """Print next steps"""
        print("\n" + "="*40)
        print("Setup completed successfully!")
        print("="*40)
        print("\nNext steps:")
        print("1. Edit .env file with your credentials")
        
        if os.name == "nt":  # Windows
            print("2. Run: venv\\Scripts\\activate")
            print("3. python main.py")
        else:  # Unix
            print("2. Run: source venv/bin/activate")
            print("3. python main.py")
        
        print("4. For tests: pytest")
        print()
    
    def run(self):
        """Run setup"""
        self.print_header()
        self.check_python()
        self.create_venv()
        self.upgrade_pip()
        self.install_requirements()
        self.setup_env_file()
        self.create_logs_directory()
        self.print_next_steps()


if __name__ == "__main__":
    setup = ProjectSetup()
    setup.run()
