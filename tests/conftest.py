import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

FIXTURES = ROOT / "fixtures"
PRODUCTS_URL = (FIXTURES / "products.html").as_uri()
FORM_URL = (FIXTURES / "form.html").as_uri()
