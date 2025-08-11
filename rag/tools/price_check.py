import requests
import pandas as pd
from typing import Optional

print("✅ hotel_query.py loaded")

def fetch_hotel_data(region: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
    """
    Fetch raw hotel data as a DataFrame.
    """
    url = f"https://d3a3137ptsskfl.cloudfront.net/group_all/{region}/{start_date}/{end_date}"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"❌ Failed to load data: {response.status_code}")
        return None

    # Print the raw JSON response to console
    print("Raw JSON response:")
    print(response.text)

    data = response.json()
    all_rows = []

    for hotel in data:
        hotel_name = hotel.get("hotelName", "Unknown Hotel")
        prices = hotel.get("prices", [])
        for entry in prices:
            row = {
                "date": entry["date"],
                "roomCode": entry["roomCode"],
                "rateCode": entry["rateCode"],
                "price": entry["price"],
                "available": entry["available"],
                "stopSell": entry["stopSell"],
                "hotelName": hotel_name,
            }
            all_rows.append(row)

    df = pd.DataFrame(all_rows)

    # Check for the 'price' column and handle its type conversion
    if 'price' in df.columns:
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        print("Successfully converted 'price' column to numeric.")
    else:
        print("WARNING: The 'price' column was not found in the fetched hotel data.")
        df['price'] = None

    # --- Start of the added robust check ---
    # Check if the 'stopSell' column exists before trying to filter.
    if 'stopSell' in df.columns:
        # Exclude hotels where stopSell is True
        df = df[df['stopSell'] != True]
    # The code will now proceed without a warning if the column is missing.
    # --- End of the added robust check ---

    # --- The price formatting line has been removed from here ---

    return df


def query_hotels(
    region: str,
    start_date: str,
    end_date: str,
    query_type: str,
    hotel_name: Optional[str] = None,
    limit: int = 10
) -> Optional[str]:
    """
    Query hotel data based on different query types:
    - "by_name": Find hotel by name
    - "top_cheapest": Get top N cheapest hotels (distinct by hotel)
    - "cheapest_prices": Sorted ascending prices with limit
    
    Returns:
        str: JSON string of filtered results
    """
    df = fetch_hotel_data(region, start_date, end_date)
    if df is None or df.empty:
        return None

    result = None

    if query_type == "by_name" and hotel_name:
        print(f"Querying for hotel by name: {hotel_name}")
        result = df[df["hotelName"].str.contains(hotel_name, case=False, na=False)]

    
    
    elif query_type == "cheapest_prices":
        print(f"Querying for cheapest prices")
        # Sort the DataFrame while 'price' is still a number
        result = df.sort_values(by="price").head(limit)
        
        # Now format the price column on the final result
        result['price'] = result['price'].apply(lambda x: f"£{x:.2f}" if pd.notnull(x) else None)
        print(result)

    else:
        print("⚠️ Invalid query type or missing parameters.")
        return None

    return result.to_json(orient='records', date_format='iso')
