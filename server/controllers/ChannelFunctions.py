import pandas as pd

#Donchian Channel function
def DONCH(high, low ,  n = 20):
    """
    Calculates the Donchian Channel using efficient pandas rolling functions.

    Args:
        high (pd.Series): Series of high prices.
        low (pd.Series): Series of low prices.
        n (int): The period for the channel calculation.

    Returns:
        tuple[pd.Series, pd.Series, pd.Series]: A tuple containing the
                                                 Highest High (Upper Band),
                                                 Middle Band, and
                                                 Lowest Low (Lower Band).
    """
    # Use pandas' rolling window functions for efficiency.
    # min_periods=1 ensures that there are no NaN values at the beginning,
    # mimicking the behavior of the original function.
    highest_high = high.rolling(window=n, min_periods=1).max()
    lowest_low = low.rolling(window=n, min_periods=1).min()

    # Calculate the middle band
    middle_band = (highest_high + lowest_low) / 2

    # Create a DataFrame to structure the output
    df = pd.DataFrame(index=high.index)
    df['Highest_high'] = highest_high
    df['Lowest_low'] = lowest_low
    df['Middle_band'] = middle_band

    return df['Highest_high'], df['Middle_band'], df['Lowest_low']

