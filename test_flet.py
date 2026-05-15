"""
Flet installation test script.

Tests if Flet is properly installed and working.
"""

import sys
import subprocess


def print_header(text):
    """Print formatted header."""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")


def test_flet_import():
    """Test Flet import."""
    print_header("Testing Flet Import")
    try:
        import flet
        print(f"✓ Flet version: {flet.__version__}")
        print(f"✓ Flet location: {flet.__file__}")
        return True
    except ImportError as e:
        print(f"✗ Error importing Flet: {e}")
        return False


def test_dependencies():
    """Test required dependencies."""
    print_header("Testing Dependencies")
    
    dependencies = {
        'fastapi': 'FastAPI',
        'uvicorn': 'Uvicorn',
        'pydantic': 'Pydantic',
        'httpx': 'HTTPX',
        'flet': 'Flet',
        'networkx': 'NetworkX',
        'matplotlib': 'Matplotlib'
    }
    
    all_ok = True
    for module, name in dependencies.items():
        try:
            mod = __import__(module)
            version = getattr(mod, '__version__', 'unknown')
            print(f"✓ {name:<20} v{version}")
        except ImportError:
            print(f"✗ {name:<20} NOT INSTALLED")
            all_ok = False
    
    return all_ok


def test_flet_ui():
    """Test Flet basic UI components."""
    print_header("Testing Flet UI Components")
    try:
        import flet as ft
        
        # Test basic components
        components = [
            ('Page', ft.Page),
            ('Container', ft.Container),
            ('Column', ft.Column),
            ('Row', ft.Row),
            ('Text', ft.Text),
            ('Button', ft.ElevatedButton),
            ('TextField', ft.TextField),
            ('Dropdown', ft.Dropdown),
            ('DataTable', ft.DataTable),
            ('NavigationRail', ft.NavigationRail)
        ]
        
        for name, component in components:
            try:
                # Try to instantiate (some may need args, but we're just testing availability)
                if name == 'Page':
                    print(f"✓ {name:<20} available")
                else:
                    obj = component()
                    print(f"✓ {name:<20} available")
            except Exception as e:
                print(f"✓ {name:<20} available (can't instantiate standalone)")
        
        return True
    except Exception as e:
        print(f"✗ Error testing Flet UI: {e}")
        return False


def test_api_client():
    """Test API client can be imported."""
    print_header("Testing API Client")
    try:
        sys.path.insert(0, '.')
        from frontend.services.api_client import APIClient
        
        print("✓ API Client imported successfully")
        
        client = APIClient()
        print(f"✓ API Client instantiated")
        print(f"✓ Base URL: {client.base_url}")
        print(f"✓ Timeout: {client.timeout}")
        
        return True
    except Exception as e:
        print(f"✗ Error testing API Client: {e}")
        return False


def main():
    """Run all tests."""
    print("\n")
    print("╔════════════════════════════════════════════════════════╗")
    print("║        SkyRoute Planner - Flet Installation Test       ║")
    print("╚════════════════════════════════════════════════════════╝")
    
    results = {
        'Flet Import': test_flet_import(),
        'Dependencies': test_dependencies(),
        'Flet UI Components': test_flet_ui(),
        'API Client': test_api_client()
    }
    
    # Summary
    print_header("Test Summary")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:<8} {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Flet is ready to use.\n")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check the errors above.\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
