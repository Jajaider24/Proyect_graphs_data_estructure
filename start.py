"""
Quick start script for SkyRoute Planner.

This script initializes and starts both the backend API and frontend.
"""

import subprocess
import os
import time
import sys
import webbrowser


def print_header(text):
    """Print formatted header."""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")


def check_dependencies():
    """Check if required packages are installed."""
    print_header("Verificando dependencias")
    
    required_packages = ['fastapi', 'uvicorn', 'flet', 'httpx']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} instalado")
        except ImportError:
            print(f"✗ {package} NO instalado")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nPaquetes faltantes: {', '.join(missing_packages)}")
        print("Ejecute: pip install -r requirements.txt")
        return False
    
    print("\n✓ Todas las dependencias están instaladas")
    return True


def start_backend():
    """Start FastAPI backend."""
    print_header("Iniciando Backend FastAPI")
    
    print("Iniciando servidor en http://localhost:8000...")
    print("API Docs disponible en http://localhost:8000/docs")
    print("\nPresione Ctrl+C en esta terminal para detener el servidor\n")
    
    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "api.main:app",
        "--reload",
        "--host",
        "127.0.0.1",
        "--port",
        "8000"
    ]
    
    subprocess.Popen(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))


def start_frontend():
    """Start Flet frontend."""
    print_header("Iniciando Frontend Flet")
    
    print("Iniciando interfaz gráfica...")
    print("Asegúrese de que el servidor Backend esté corriendo\n")
    
    time.sleep(3)  # Wait for backend to start
    
    cmd = [
        sys.executable,
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "main.py")
    ]
    
    subprocess.Popen(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))


def main():
    """Main entry point."""
    print("\n")
    print("╔════════════════════════════════════════════════════════╗")
    print("║           SkyRoute Planner - Quick Start               ║")
    print("║                                                        ║")
    print("║      Sistema de Planificación de Rutas Aéreas         ║")
    print("╚════════════════════════════════════════════════════════╝\n")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Start backend
    print_header("Seleccione qué desea iniciar")
    print("1. Iniciar Solo Backend (FastAPI)")
    print("2. Iniciar Solo Frontend (Flet)")
    print("3. Iniciar Backend y Frontend")
    print("0. Salir\n")
    
    choice = input("Seleccione una opción (0-3): ").strip()
    
    if choice == "1":
        start_backend()
    elif choice == "2":
        print("\n⚠️  Asegúrese de que el servidor Backend esté corriendo en http://localhost:8000")
        time.sleep(2)
        start_frontend()
    elif choice == "3":
        start_backend()
        time.sleep(5)  # Wait for backend to fully start
        start_frontend()
    else:
        print("Saliendo...")
        sys.exit(0)
    
    # Keep script running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nAplicación finalizada.")


if __name__ == "__main__":
    main()
