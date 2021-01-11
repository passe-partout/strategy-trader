import pandas as pd
import datetime as dt
from util import get_data
from matplotlib import pyplot as plt


def author():
    return ''

# returns a data frame of indicators
def get_indicators(prices):

    # Initializing an indicators df
    df_indicators = pd.DataFrame(index=prices.index)
    df_indicators['Price'] = prices

    # Indicator 1: SMA & Price/SMA
    sma = prices.rolling(window=10).mean()
    df_indicators['SMA'] = sma
    df_indicators['Price/SMA'] = prices / sma

    # Indicator 2: Bollinger Bands
    std = prices.rolling(window=10).std()
    bb_upper = sma + 2 * std
    bb_lower = sma - 2 * std
    bb_value = (prices - sma) / (2 * std)
    df_indicators['BB Upper'] = bb_upper
    df_indicators['BB Lower'] = bb_lower
    df_indicators['BB Value'] = bb_value

    # Indicator 3: Momentum
    momentum = prices / prices.shift(10) - 1
    df_indicators['Momentum'] = momentum

    df_indicators.dropna()

    return df_indicators


# def test_code():
#     in_sample_sd = dt.datetime(2008, 1, 1)
#     in_sample_ed = dt.datetime(2009, 12, 31)
#     in_sample_dates = pd.date_range(in_sample_sd, in_sample_ed)
#     df_in_sample = get_data(["JPM"], in_sample_dates)
#
#     # Normalization
#     df_in_sample = df_in_sample / df_in_sample.iloc[0, :]
#     df_indicators = get_indicators(df_in_sample[["JPM"]])
#
#     # Plot SMA
#     df_indicators[['Price', 'SMA', 'Price/SMA']].plot(grid=True, title='Simple Moving Average(SMA)', use_index=True, figsize=(20, 10))
#     plt.xlabel("Date")
#     plt.ylabel("Normalized Value")
#     plt.tight_layout()
#     plt.savefig("1.SMA.png")
#
#     # Plot Bollinger Bands with prices and SMA
#     df_indicators[['Price', 'SMA', 'BB Upper', 'BB Lower', 'BB Value']].plot(grid=True, title='Bollinger Bands', use_index=True, figsize=(20, 10))
#     plt.xlabel("Date")
#     plt.ylabel("Normalized Value")
#     plt.tight_layout()
#     plt.savefig("2.BB.png")
#
#     # Plot Momentum
#     df_indicators[['Price', 'Momentum']].plot(grid=True, title='Momentum', use_index=True, figsize=(20, 10))
#     plt.xlabel("Date")
#     plt.ylabel("Normalized Value")
#     plt.tight_layout()
#     plt.savefig("3.Momentum.png")
#
#
# if __name__ == "__main__":
#     test_code()