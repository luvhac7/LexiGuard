import json
import os
import sys
from case_comparer import detect_bias_juris_ai

# Mock data for testing
docs = [
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
    },
    {
      "tid": 173128227,
      "catids": None,
      "doctype": 1133,
      "publishdate": "2024-04-30",
      "authorid": None,
      "bench": None,
      "title": "J.J. Clinic & Nursing Home & Anr. vs Kumari Richa Singh on 30 April, 2024",
      "numcites": 12,
      "numcitedby": 0,
      "headline": "SUBHASH CHANDRA\n\n \n\n \n\n \n\n  1.      This appeal <b>under</b>  section 15  of the <b>Consumer</b> <b>Protection</b> <b>Act</b>, 1986 (in short, the '<b>Act</b>') challenges the order dated ... Supreme Court with regard to <b>medical</b> <b>negligence</b> <b>under</b> the  <b>Consumer</b> <b>Protection</b> <b>Act</b> .  In  Jacob Matthew  (supra), the Apex Court has held that: \n \n \n\n         <b>Negligence</b>",
      "docsize": 26233,
      "fragment": True,
      "docsource": "National Consumer Disputes Redressal"
    }
]

try:
    print("Running bias detection...")
    result = detect_bias_juris_ai(docs)
    print("\n--- BIAS DETECTION RESULT ---\n")
    print(json.dumps(result, indent=2))
except Exception as e:
    print(f"Error: {e}")
