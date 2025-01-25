from pathlib import Path
import sys

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# Configure pytest
def pytest_configure(config):
    config.addinivalue_line("markers", "integration: mark test as integration test")
