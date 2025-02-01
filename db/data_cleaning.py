import pandas as pd


def calculate_spy_changes(spy_hourly_df):
    """
    Calculate SPY percentage changes, total volume, and additional metrics for each day.

    Args:
        spy_hourly_df (pd.DataFrame): DataFrame with SPY hourly data including 'Close', 'Volume',
                                      and ideally 'Open' columns for the next-day hourly returns calculation.

    Returns:
        pd.DataFrame: 
            DataFrame with daily metrics for the last 1, 2, 3, and 5 trading days,
            including next-day hourly returns and open indicators.
    """
    # Ensure the datetime index is in UTC format and sorted
    spy_hourly_df.index = pd.to_datetime(spy_hourly_df.index, utc=True)
    spy_hourly_df = spy_hourly_df.sort_index()

    # Resample the data to daily frequency:
    # - last 'Close' of each day
    # - sum of 'Volume' within the day
    # NOTE: If you have specific market hours (e.g., 9:30–16:00), you may want to filter
    #       or handle partial days differently.
    daily_df = (
        spy_hourly_df
        .resample('1D')
        .agg({'Close': 'last', 'Volume': 'sum'})
        .dropna()  # Drop days without a last close (incomplete days)
    )

    # Prepare the DataFrame to hold daily metrics
    metrics_df = pd.DataFrame(index=daily_df.index)

    # Calculate metrics for each day
    for i in range(1, len(daily_df)):
        current_day = daily_df.iloc[: i + 1]

        # Metrics for different periods
        for period in [1, 2, 3, 5]:
            if i >= period:
                start_close = current_day['Close'].iloc[-(period + 1)]
                end_close = current_day['Close'].iloc[-1]
                change = (end_close / start_close - 1) * 100  # percentage change
                volume_sum = current_day['Volume'].iloc[-period:].sum()

                metrics_df.loc[current_day.index[-1], f'Change_{period}D_%'] = round(change, 2)
                metrics_df.loc[current_day.index[-1], f'Volume_{period}D'] = volume_sum
            else:
                metrics_df.loc[current_day.index[-1], f'Change_{period}D_%'] = None
                metrics_df.loc[current_day.index[-1], f'Volume_{period}D'] = None

        # Next-day hourly returns and open indicators
        if i + 1 < len(daily_df):
            next_day = daily_df.index[i + 1]
            next_day_data = spy_hourly_df[next_day: next_day + pd.Timedelta(days=1)]

            if 'Open' not in next_day_data.columns:
                # If Open is missing, skip or add fallback
                metrics_df.loc[current_day.index[-1], 'NextDay_Hour1_Return_%'] = None
                metrics_df.loc[current_day.index[-1], 'NextDay_Hour1_Open_Positive'] = None
                # Repeat for Hour2, Hour3 as needed
                continue

            for hour in range(1, 4):  # First 3 hours
                if len(next_day_data) >= hour:
                    open_price = next_day_data['Open'].iloc[0]
                    hour_close = next_day_data['Close'].iloc[hour - 1]
                    hourly_return = (hour_close / open_price - 1) * 100

                    metrics_df.loc[
                        current_day.index[-1], f'NextDay_Hour{hour}_Return_%'
                    ] = round(hourly_return, 2)
                    metrics_df.loc[
                        current_day.index[-1], f'NextDay_Hour{hour}_Open_Positive'
                    ] = int(hourly_return > 0)
                else:
                    metrics_df.loc[current_day.index[-1], f'NextDay_Hour{hour}_Return_%'] = None
                    metrics_df.loc[current_day.index[-1], f'NextDay_Hour{hour}_Open_Positive'] = None

    return metrics_df


def calculate_other_symbols(file_path, symbol, periods):
    """
    Calculates percentage change and (optionally) rolling volume for a given symbol
    over specified rolling periods in hours, then aggregates those on a daily basis.

    Args:
        file_path (str): Path to the CSV file containing hourly data with 'Close'
                         and (optionally) 'Volume' columns.
        symbol (str): Symbol identifier (e.g., 'EURUSD=X', '^FTSE', etc.).
        periods (list): List of integers representing the number of hours
                        for rolling/periodic calculations.

    Returns:
        pd.DataFrame:
            Daily DataFrame containing the last value of the rolling percentage change
            and, if available, the sum of volumes for those periods.
    """
    df = pd.read_csv(file_path, index_col=0, parse_dates=True)
    df.index = pd.to_datetime(df.index, utc=True)
    df = df.sort_index()

    # Create a daily index based on the mean (or any other aggregator) to ensure we have
    # a daily frequency. We'll store results in this new DataFrame.
    daily_index = df.resample('1D').mean().index
    metrics = pd.DataFrame(index=daily_index)

    # Calculate % change and volume over the given periods
    for period in periods:
        change = df['Close'].pct_change(periods=period) * 100
        metrics[f'{symbol}_Change_{period}H_%'] = change.resample('1D').last()

    return metrics


def merge_data(spy_df, other_dfs):
    """
    Merge multiple DataFrames into a single DataFrame using merge_asof.

    Args:
        spy_df (pd.DataFrame): DataFrame for SPY metrics (daily frequency).
        other_dfs (list):      List of other DataFrames (also daily) to merge.

    Returns:
        pd.DataFrame:
            A merged DataFrame containing SPY metrics and the metrics from each
            of the other DataFrames, aligned by date using 'backward' fill.
    """
    merged_df = spy_df.copy()
    merged_df = merged_df.sort_index()

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


if __name__ == "__main__":
    # Updated dictionary to map symbol -> file path
    file_paths = {
        "EURUSD=X": r"C:\Users\pc\Algo\data\eurusd_hourly.csv",
        "^FTSE":    r"C:\Users\pc\Algo\data\ftse_hourly.csv",
        "SPY":      r"C:\Users\pc\Algo\data\spy_hourly.csv",
        "^NQSG":    r"C:\Users\pc\Algo\data\nqsg_hourly.csv"
    }

    # --- Calculate SPY metrics ---
    spy_hourly_df = pd.read_csv(
        file_paths["SPY"],   # Use symbol as the key
        index_col=0,
        parse_dates=True
    )
    spy_metrics_df = calculate_spy_changes(spy_hourly_df)

    # --- Calculate metrics for other symbols ---
    eurusd_metrics = calculate_other_symbols(
        file_paths["EURUSD=X"],
        "EURUSD=X",
        [1, 7, 24]
    )
    ftse_metrics = calculate_other_symbols(
        file_paths["^FTSE"],
        "^FTSE",
        [1, 24]
    )
    nqsg_metrics = calculate_other_symbols(
        file_paths["^NQSG"],
        "^NQSG",
        [24]
    )

    # --- Merge all data ---
    merged_df = merge_data(spy_metrics_df, [eurusd_metrics, ftse_metrics, nqsg_metrics])

    # Output merged DataFrame
    print(merged_df)
    # Export merged DataFrame to CSV
    merged_df.to_csv(r"C:\Users\pc\Algo\data\merged_data.csv")

    # Example usage for SPY summary:
    spy_hourly_df = pd.read_csv(
        file_paths["SPY"],
        index_col=0,
        parse_dates=True
    )
    spy_hourly_df.index = pd.to_datetime(spy_hourly_df.index, utc=True)
    spy_summary_df = calculate_spy_changes(spy_hourly_df)
    print(spy_summary_df)
    spy_summary_df.to_csv(r"C:\Users\pc\Algo\data\spy_summary_df.csv")
