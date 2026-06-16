import sys
import os
import json
sys.path.append(os.getcwd())

from app.database import get_all_companies
companies = get_all_companies()
if companies:
    print(json.dumps(companies[0], indent=2))
