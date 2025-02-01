import pandas as pd

def calculate_spy_changes(spy_hourly_df):
    """
    Calculate SPY percentage changes, total volume, and additional metrics for each day.

    Args:
        spy_hourly_df (pd.DataFrame): DataFrame with SPY hourly data including 'Close' and 'Volume' columns.

    Returns:
        pd.DataFrame: DataFrame with daily metrics for the last 1, 2, 3, and 5 trading days,
                      including next-day hourly returns and open indicators.
    """
    # Ensure the datetime index is in UTC format and sorted
    spy_hourly_df.index = pd.to_datetime(spy_hourly_df.index, utc=True)
    spy_hourly_df = spy_hourly_df.sort_index()

    # Resample the data to daily frequency (using the last close of each day)
    daily_df = spy_hourly_df.resample('1D').agg({
        'Close': 'last',
        'Volume': 'sum'
    }).dropna()  # Drop incomplete days

    # Prepare the DataFrame to hold daily metrics
    metrics_df = pd.DataFrame(index=daily_df.index)

    # Calculate metrics for each day
    for i in range(1, len(daily_df)):
        current_day = daily_df.iloc[:i+1]

        # Metrics for different periods
        for period in [1, 2, 3, 5]:
            if i >= period:
                change = ((current_day['Close'].iloc[-1] / current_day['Close'].iloc[-(period+1)]) - 1) * 100
                volume = current_day['Volume'].iloc[-period:].sum()

                metrics_df.loc[current_day.index[-1], f'Change_{period}D_%'] = round(change, 2)
                metrics_df.loc[current_day.index[-1], f'Volume_{period}D'] = volume
            else:
                metrics_df.loc[current_day.index[-1], f'Change_{period}D_%'] = 'N/A'
                metrics_df.loc[current_day.index[-1], f'Volume_{period}D'] = 'N/A'

        # Next day hourly returns and open indicators
        if i + 1 < len(daily_df):
            next_day = daily_df.index[i + 1]
            next_day_data = spy_hourly_df[next_day:next_day + pd.Timedelta(days=1)]

            for hour in range(1, 4):  # First, second, and third hours
                if len(next_day_data) >= hour:
                    open_price = next_day_data['Close'].iloc[0]
                    hour_close = next_day_data['Close'].iloc[hour - 1]
                    hourly_return = ((hour_close / open_price) - 1) * 100

                    metrics_df.loc[current_day.index[-1], f'NextDay_Hour{hour}_Return_%'] = round(hourly_return, 2)
                    metrics_df.loc[current_day.index[-1], f'NextDay_Hour{hour}_Open_Positive'] = int(hourly_return > 0)
                else:
                    metrics_df.loc[current_day.index[-1], f'NextDay_Hour{hour}_Return_%'] = 'N/A'
                    metrics_df.loc[current_day.index[-1], f'NextDay_Hour{hour}_Open_Positive'] = 'N/A'

    return metrics_df

# Example usage:
# Assuming `spy_hourly_df` contains hourly data with DateTime index, 'Close', and 'Volume' columns
spy_hourly_df = pd.read_csv(r"C:\Users\pc\Algo\data\spy_hourly.csv", index_col=0, parse_dates=True)
spy_hourly_df.index = pd.to_datetime(spy_hourly_df.index, utc=True)
spy_summary_df = calculate_spy_changes(spy_hourly_df)
print(spy_summary_df)



spy_summary_df.to_csv(r"C:\Users\pc\Algo\data\spy_summary_df.csv")