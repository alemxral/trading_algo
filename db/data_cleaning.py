import pandas as pd

def read_hourly_data(filepath, utc=True):
    """
    Reads a CSV file containing hourly data into a DataFrame,
    sets the index to a DateTimeIndex, and sorts by the index.

    Args:
        filepath (str): Path to the CSV file.
        utc (bool): Whether to convert the datetime index to UTC.

    Returns:
        pd.DataFrame: A sorted DataFrame with a DateTimeIndex.
    """
    df = pd.read_csv(filepath, index_col=0, parse_dates=True)
    if utc:
        df.index = pd.to_datetime(df.index, utc=True)
    return df.sort_index()


def calculate_spy_changes(spy_hourly_df):
    """
    Calculate SPY daily close, percentage changes (for price and volume),
    and next-day hourly returns.

    For price, for each period (1, 2, 3, 5 days):
        Price change = (Current day's close / close from 'p' days ago - 1) * 100

    For volume, for each period (p days) the volume change percentage is computed
    by comparing the sum of volumes for the last p days to the sum for the previous p days:
        Volume change = ( (sum of last p days) / (sum of previous p days) - 1 ) * 100

    Args:
        spy_hourly_df (pd.DataFrame): SPY hourly data with 'Close', 'Volume',
                                      and ideally 'Open' (for next-day returns).

    Returns:
        pd.DataFrame:
            Daily DataFrame with columns:
                - SPY_Daily_Close
                - Change_{p}D_%       (price change over p days)
                - Volume_{p}D_%       (volume change percentage over p days)
                - NextDay_Hour{h}_Return_% (hourly return for hour h on the next day)
                - NextDay_Hour{h}_Open_Positive (indicator if the return is positive)
    """
    # Resample hourly data to daily data: last close and sum of volume
    daily_df = (
        spy_hourly_df
        .resample('1D')
        .agg({'Close': 'last', 'Volume': 'sum'})
        .dropna()  # Drop days that are missing a closing price
    )

    metrics_df = pd.DataFrame(index=daily_df.index)
    metrics_df['SPY_Daily_Close'] = daily_df['Close']

    # Calculate price and volume changes for each day and period.
    for i in range(1, len(daily_df)):
        current_slice = daily_df.iloc[: i + 1]

        for period in [1, 2, 3, 5]:
            # --- Price Change ---
            if i >= period:
                start_close = current_slice['Close'].iloc[-(period + 1)]
                end_close = current_slice['Close'].iloc[-1]
                price_change = (end_close / start_close - 1) * 100
                metrics_df.loc[current_slice.index[-1], f'Change_{period}D_%'] = round(price_change, 2)
            else:
                metrics_df.loc[current_slice.index[-1], f'Change_{period}D_%'] = None

            # --- Volume Change (Percentage) ---
            # Require at least 2*period days to calculate a percentage change
            if i + 1 >= 2 * period:
                current_vol = current_slice['Volume'].iloc[-period:].sum()
                previous_vol = current_slice['Volume'].iloc[-(2 * period):-period].sum()
                if previous_vol != 0:
                    vol_change = (current_vol / previous_vol - 1) * 100
                else:
                    vol_change = None
                metrics_df.loc[current_slice.index[-1], f'Volume_{period}D_%'] = round(vol_change, 2) if vol_change is not None else None
            else:
                metrics_df.loc[current_slice.index[-1], f'Volume_{period}D_%'] = None

        # --- Next-day Hourly Returns ---
        if i + 1 < len(daily_df):
            next_day_date = daily_df.index[i + 1]
            next_day_data = spy_hourly_df[next_day_date: next_day_date + pd.Timedelta(days=1)]

            if 'Open' not in next_day_data.columns:
                # If no Open data, set next-day hourly return fields to None
                for hour in range(1, 4):
                    metrics_df.loc[current_slice.index[-1], f'NextDay_Hour{hour}_Return_%'] = None
                    metrics_df.loc[current_slice.index[-1], f'NextDay_Hour{hour}_Open_Positive'] = None
            else:
                for hour in range(1, 4):
                    if len(next_day_data) >= hour:
                        open_price = next_day_data['Open'].iloc[0]
                        hour_close = next_day_data['Close'].iloc[hour - 1]
                        hourly_return = (hour_close / open_price - 1) * 100
                        metrics_df.loc[current_slice.index[-1], f'NextDay_Hour{hour}_Return_%'] = round(hourly_return, 2)
                        metrics_df.loc[current_slice.index[-1], f'NextDay_Hour{hour}_Open_Positive'] = int(hourly_return > 0)
                    else:
                        metrics_df.loc[current_slice.index[-1], f'NextDay_Hour{hour}_Return_%'] = None
                        metrics_df.loc[current_slice.index[-1], f'NextDay_Hour{hour}_Open_Positive'] = None

    return metrics_df


def calculate_symbol_changes(filepath, symbol, periods):
    """
    Calculates daily close and rolling percentage changes (over specified hours)
    for non-SPY symbols.

    Args:
        filepath (str): Path to the CSV with hourly data (must contain 'Close').
        symbol (str): Symbol identifier (e.g., 'EURUSD=X', '^FTSE').
        periods (list): List of integers (hours) for rolling percentage changes.

    Returns:
        pd.DataFrame:
            Daily DataFrame with columns:
                - {symbol}_Daily_Close
                - {symbol}_Change_{period}H_%
    """
    df = read_hourly_data(filepath)
    daily_index = df.resample('1D').mean().index
    metrics = pd.DataFrame(index=daily_index)

    # Daily close price
    daily_close = df['Close'].resample('1D').last()
    metrics[f'{symbol}_Daily_Close'] = daily_close

    # Rolling percentage changes for specified hours
    for period in periods:
        hourly_change = df['Close'].pct_change(periods=period) * 100
        metrics[f'{symbol}_Change_{period}H_%'] = hourly_change.resample('1D').last()

    return metrics


def merge_data(spy_df, other_dfs):
    """
    Merge multiple daily DataFrames using a time-based merge_asof.

    Args:
        spy_df (pd.DataFrame): SPY DataFrame (daily frequency).
        other_dfs (list): List of daily DataFrames for other symbols.

    Returns:
        pd.DataFrame: A merged daily DataFrame.
    """
    merged_df = spy_df.copy().sort_index()
    for df in other_dfs:
        df = df.sort_index()
        merged_df = pd.merge_asof(
            merged_df,
            df,
            left_index=True,
            right_index=True,
            direction='backward'
        )
    return merged_df


def fill_missing_values(df):
    """
    Fill missing values in the DataFrame by propagating the last valid observation forward.
    This fills empty fields with the last available value up to that date.
    
    Args:
        df (pd.DataFrame): DataFrame with potential missing values.
    
    Returns:
        pd.DataFrame: DataFrame with missing values filled.
    """
    return df.fillna(method='ffill')


def main():
    """
    Main execution flow:
      1) Define file paths.
      2) Calculate SPY changes (price and volume).
      3) Calculate changes for other symbols.
      4) Merge the data.
      5) Fill missing values.
      6) Export merged data to CSV.
    """
    # Map symbol -> file path
    file_paths = {
        "EURUSD=X": r"C:\Users\pc\Algo\data\eurusd_hourly.csv",
        "^FTSE":    r"C:\Users\pc\Algo\data\ftse_hourly.csv",
        "SPY":      r"C:\Users\pc\Algo\data\spy_hourly.csv",
        "^NQSG":    r"C:\Users\pc\Algo\data\nqsg_hourly.csv"
    }

    # 1) Calculate SPY metrics
    spy_hourly_df = read_hourly_data(file_paths["SPY"])
    spy_metrics_df = calculate_spy_changes(spy_hourly_df)

    # 2) Calculate metrics for other symbols (volume not included)
    eurusd_metrics = calculate_symbol_changes(file_paths["EURUSD=X"], "EURUSD=X", [1, 7, 24])
    ftse_metrics = calculate_symbol_changes(file_paths["^FTSE"], "^FTSE", [1, 24])
    nqsg_metrics = calculate_symbol_changes(file_paths["^NQSG"], "^NQSG", [24])

    # 3) Merge all DataFrames
    merged_df = merge_data(spy_metrics_df, [eurusd_metrics, ftse_metrics, nqsg_metrics])

    # 4) Fill missing values with the last available value (forward fill)
    merged_df = fill_missing_values(merged_df)

    # 5) Preview & export merged DataFrame
    print(merged_df)
    merged_df.to_csv(r"C:\Users\pc\Algo\data\merged_data.csv")

    # Example: Export just SPY summary
    spy_summary_df = calculate_spy_changes(spy_hourly_df)
    print(spy_summary_df)
    spy_summary_df.to_csv(r"C:\Users\pc\Algo\data\spy_summary_df.csv")


if __name__ == "__main__":
    main()
