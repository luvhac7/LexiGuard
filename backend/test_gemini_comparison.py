
import os
import json
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add current directory to sys.path to import case_comparer
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
# Try loading from parent directory .env if not found in current
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    print(f"Loading .env from {env_path}")
    load_dotenv(env_path)
else:
    print(f"Warning: .env not found at {env_path}")

try:
    from case_comparer import compare_cases_juris_ai
except ImportError as e:
    print(f"Error importing case_comparer: {e}")
    sys.exit(1)

# Test data provided by user
docs = [
    {
      "tid": 61302014,
      "catids": [0],
      "doctype": 1195,
      "publishdate": "2010-05-26",
      "authorid": None,
      "bench": None,
      "title": "Dr.Mahesh Avinash Joshi, vs Balasaheb Shankar Killedar, on 26 May, 2010",
      "numcites": 2,
      "numcitedby": 0,
      "headline": "Appellants that they were \nnot guilty of <b>medical</b> <b>negligence</b>.  <b>Medical</b> <b>negligence</b> as contemplated <b>under</b> \n <b>Consumer</b> <b>Protection</b> <b>Act</b>  rather in the area of torts is different ... liability they are facing for the <b>medical</b> <b>negligence</b> <b>under</b>  <b>Consumer</b> \n<b>Protection</b> <b>Act</b> .  \n  \n\n\n \n \n\n\n 8)           \n\n <b>Under</b> \n<b>Consumer</b> <b>Protection</b> <b>Act</b> , <b>medical</b> professionals can be imposed with compensation",
      "docsize": 24170,
      "fragment": True,
      "docsource": "State Consumer Disputes Redressal Commission"
    },
    {
      "tid": 1009050,
      "catids": [409],
      "doctype": 1133,
      "publishdate": "2007-08-10",
      "authorid": None,
      "bench": None,
      "title": "Dr. Sathy M. Pillai vs S. Sharma on 10 August, 2007",
      "numcites": 4,
      "numcitedby": 3,
      "headline": " Dr. Sathy M. Pillai vs S. Sharma on 10 August, 2007 \n\n   \n \n \n \n \n \n NATIONAL <b>CONSUMER</b> DISPUTES REDRESSAL",
      "docsize": 55194,
      "fragment": True,
      "docsource": "National Consumer Disputes Redressal"
    }
]

print("Starting comparison...")
try:
    result = compare_cases_juris_ai(docs)
    print("\n--- Result ---\n")
    print(json.dumps(result, indent=2))
except Exception as e:
    print(f"\nError during comparison: {e}")
