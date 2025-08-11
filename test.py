# test_price_check.py
from rag.tools.price_check import price_check

result = price_check("08-05-2025", "08-10-2025")

if result:
    print("✅ Success!")
    print(result[:50])  # Print only first 500 chars of JSON
else:
    print("❌ No data returned.")
