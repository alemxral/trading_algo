
from trading_algo.utils.dependencies import yf
import trading_algo.utils.dependencies as pd



ticker = "^NQSG"
df = yf.download(
    tickers=ticker,
    period="730d",       # ~2 years of data if available
    interval="1h",       # Hourly
    auto_adjust=True
)

print(df.head())
print(df.tail())



# Save to CSV
df.to_csv(r"C:\Users\pc\Algo\trading_algo\data\^NQSG_hourly.csv")
