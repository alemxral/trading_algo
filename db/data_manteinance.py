import yfinance as yf
import pandas as pd
import os
from datetime import datetime, timedelta

# Import the new Git module
import trading_algo.main.git_operations as git_operations 

# --- CONFIGURATION ---
files_to_update = {
    r"C:\Users\pc\Algo\trading_algo\data\eurusd_hourly.csv": "EURUSD=X",
    r"C:\Users\pc\Algo\trading_algo\data\ftse_hourly.csv": "^FTSE",
    r"C:\Users\pc\Algo\trading_algo\data\spy_hourly.csv": "SPY",
    r"C:\Users\pc\Algo\trading_algo\data\nqsg_hourly.csv": "^NQSG"
}

# --- FUNCTION TO FETCH AND UPDATE DATA ---
def update_data(file_name, ticker):
    print(f"\n[INFO] Updating data for {ticker}...")

    # Check if the file exists
    if os.path.exists(file_name):
        existing_data = pd.read_csv(file_name, index_col=0, parse_dates=True)
        last_timestamp = existing_data.index[-1]
        start_date = last_timestamp + timedelta(hours=1)
    else:
        print(f"[WARN] {file_name} not found. Fetching full history instead.")
        existing_data = pd.DataFrame()
        start_date = datetime.now() - timedelta(days=730)

    new_data = yf.download(
        tickers=ticker,
        start=start_date.strftime('%Y-%m-%d'),
        interval="1h",
        progress=False,
        auto_adjust=True
    )

    if new_data.empty:
        print(f"[INFO] No new data found for {ticker}.")
        return

    updated_data = pd.concat([existing_data, new_data])
    updated_data = updated_data[~updated_data.index.duplicated(keep='last')]
    updated_data.sort_index(inplace=True)
    updated_data.to_csv(file_name)

    print(f"[SUCCESS] {file_name} updated with {len(new_data)} new rows.")

# --- MAIN MAINTENANCE FUNCTION ---
def run_maintenance():
    print(f"\n=== Running Data Maintenance: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")

    updated_files = []
    for file, ticker in files_to_update.items():
        update_data(file, ticker)
        updated_files.append(file)  # Track updated files

    print("=== Data Maintenance Complete ===")

    # Trigger Git operations after updates
    git_operations.commit_and_push(updated_files)

if __name__ == "__main__":
    print("📈 Data Maintenance Module Started.")
    # run_maintenance()
    git_operations.commit_and_push()


