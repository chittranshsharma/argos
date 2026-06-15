import sys
import os
import asyncio
sys.path.append(os.getcwd())

from app.database import get_company_by_id
from app.main import run_monitoring_for_company
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")

company = get_company_by_id('ab4d1d45-dc2a-441f-8d85-c65e1d14cb99')
if company:
    print(f"Running monitoring for {company['name']}...")
    run_monitoring_for_company(company)
else:
    print("Company not found.")
