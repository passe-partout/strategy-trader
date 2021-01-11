import datetime as dt
from matplotlib import pyplot as plt
import pandas as pd
from util import get_data
from indicators import get_indicators
from marketsimcode import compute_portvals
# from TheoreticallyOptimalStrategy import TheoreticallyOptimalStrategy

def author():
    return ''

class ManualStrategy(object):

    def testPolicy(self, symbol="JPM", sd=dt.datetime(2008, 1, 1), ed=dt.datetime(2009, 12, 31), sv=100000):

        # Initialization
        dates = pd.date_range(sd, ed)
        data = get_data([symbol], dates)
        prices = data[symbol]
        prices = prices / prices.iloc[0]
        daily_rets = prices / prices.shift(1) - 1
        indices = data["SPY"]
        indices = indices / indices.iloc[0]
        trading_days = indices.index
        indicators = get_indicators(prices.to_frame(symbol))
        bb_ratio = indicators["BB Value"]
        sma_ratio = indicators["Price/SMA"]
        momentum = indicators["Momentum"]

        holding = 0
        df_trades = pd.Series(index=trading_days)
        for i in df_trades.index:
            if bb_ratio.loc[i] > 0.9 and sma_ratio.loc[i] > 1.02 and momentum.loc[i] > 0.05:
                df_trades.loc[i] = {-1000: 0, 0: -1000, 1000: -2000,}.get(holding)
            elif bb_ratio.loc[i] < -0.9 and sma_ratio.loc[i] < 0.98 and momentum.loc[i] < -0.01:
                df_trades.loc[i] = {-1000: 2000, 0: 1000, 1000: 0,}.get(holding)
            else:
                df_trades.loc[i] = 0
            holding += df_trades.loc[i]

        return df_trades.to_frame(symbol)


# def test_code():
#
#     ms = ManualStrategy()
#     symbol = "JPM"
#     sv = 100000
#
#     # In-sample testing
#     in_sample_sd = dt.datetime(2008, 1, 1)
#     in_sample_ed = dt.datetime(2009, 12, 31)
#     trading_days_in = get_data(["SPY"], dates=pd.date_range(in_sample_sd, in_sample_ed)).index
#
#     # In-sample Benchmark
#     df_bm_in = pd.DataFrame([1000] + [0] * (len(trading_days_in) - 1), columns=[symbol], index=trading_days_in)
#     bm_in = compute_portvals(df_bm_in, start_val=sv, commission=9.95, impact=0.005)
#     bm_in = bm_in / bm_in.iloc[0, :]
#
#     # In-sample Manual Strategy
#     df_trades_in = ms.testPolicy(symbol=symbol, sd=in_sample_sd, ed=in_sample_ed, sv=sv)
#     portvals_in = compute_portvals(df_trades_in, start_val=sv, commission=9.95, impact=0.005)
#     portvals_in = portvals_in / portvals_in.iloc[0, :]
#
#     # Stats for In-Sample Benchmark
#     cum_ret_bm_in = (bm_in.iloc[-1, 0] / bm_in.iloc[0, 0]) - 1
#     daily_ret_bm_in = (bm_in / bm_in.shift(1)) - 1
#     std_daily_ret_bm_in = daily_ret_bm_in.iloc[1:, 0].std()
#     avg_daily_ret_bm_in = daily_ret_bm_in.iloc[1:, 0].mean()
#
#     # Stats for In-Sample Manual Strategy
#     cum_ret_in = (portvals_in.iloc[-1, 0] / portvals_in.iloc[0, 0]) - 1
#     daily_ret_in = (portvals_in / portvals_in.shift(1)) - 1
#     std_daily_ret_in = daily_ret_in.iloc[1:, 0].std()
#     avg_daily_ret_in = daily_ret_in.iloc[1:, 0].mean()
#
#     # Print stats of In-Sample Benchmark and In-sample Manual Strategy Portfolio values:
#     print()
#     print("***************** In-Sample Comparison **********************")
#     print()
#     print(f"Date Range: {in_sample_sd.date()} to {in_sample_ed.date()}")
#     print()
#     print(f"Cumulative Return of Benchmark Portfolio: {cum_ret_bm_in}")
#     print(f"Cumulative Return of Manual Strategy Portfolio: {cum_ret_in}")
#     print()
#     print(f"Standard Deviation of Benchmark Portfolio: {std_daily_ret_bm_in}")
#     print(f"Standard Deviation of Manual Strategy Portfolio: {std_daily_ret_in}")
#     print()
#     print(f"Average Daily Return of Benchmark Portfolio: {avg_daily_ret_bm_in}")
#     print(f"Average Daily Return of Manual Strategy Portfolio: {avg_daily_ret_in}")
#     print()
#     print(f"Final Portfolio Value: {portvals_in.iloc[-1, 0]}")
#     print()
#
#     # Plot in-sample comparison chart
#     fig, ax = plt.subplots()
#     bm_in.plot(ax=ax, color="green")
#     portvals_in.plot(ax=ax, color="red")
#     plt.legend(["Benchmark", "Manual Strategy"])
#     plt.title("Manual Strategy vs. Benchmark (In-Sample)")
#     plt.xlabel("Date")
#     plt.ylabel("Normalized Value")
#     for day, order in df_trades_in[df_trades_in[symbol] != 0].iterrows():
#         if order[symbol] < 0:
#             ax.axvline(day, color="black")
#         elif order[symbol] > 0:
#             ax.axvline(day, color="blue")
#     plt.grid()
#     plt.tight_layout()
#     plt.savefig("5.Comparison_in.png")
#
# ########################################################################################################################
#
#     # Out-of-sample testing
#     out_sample_sd = dt.datetime(2010, 1, 1)
#     out_sample_ed = dt.datetime(2011, 12, 31)
#     trading_days_out = get_data(["SPY"], dates=pd.date_range(out_sample_sd, out_sample_ed)).index
#
#     # Benchmark
#     df_bm_out = pd.DataFrame([1000] + [0] * (len(trading_days_out) - 1), columns=[symbol], index=trading_days_out)
#     bm_out = compute_portvals(df_bm_out, start_val=sv, commission=9.95, impact=0.005)
#     bm_out = bm_out / bm_out.iloc[0, :]
#
#     # Out-of-sample Manual Strategy
#     df_trades_out = ms.testPolicy(symbol=symbol, sd=out_sample_sd, ed=out_sample_ed, sv=sv)
#     portvals_out = compute_portvals(df_trades_out, start_val=sv, commission=9.95, impact=0.005)
#     portvals_out /= portvals_out.iloc[0, :]
#
#     # Stats for Out-of-Sample Benchmark
#     cum_ret_bm_out = (bm_out.iloc[-1, 0] / bm_out.iloc[0, 0]) - 1
#     daily_ret_bm_out = (bm_out / bm_out.shift(1)) - 1
#     std_daily_ret_bm_out = daily_ret_bm_out.iloc[1:, 0].std()
#     avg_daily_ret_bm_out = daily_ret_bm_out.iloc[1:, 0].mean()
#
#     # Stats for Out-of-Sample Manual Strategy
#     cum_ret_out = (portvals_out.iloc[-1, 0] / portvals_out.iloc[0, 0]) - 1
#     daily_ret_out = (portvals_out / portvals_out.shift(1)) - 1
#     std_daily_ret_out = daily_ret_out.iloc[1:, 0].std()
#     avg_daily_ret_out = daily_ret_out.iloc[1:, 0].mean()
#
#     # Print stats of Out-of-Sample Benchmark and Theoretically Optimal Portfolio values:
#     print("***************** Out-of-Sample Comparison **********************")
#     print()
#     print(f"Date Range: {out_sample_sd.date()} to {out_sample_ed.date()}")
#     print()
#     print(f"Cumulative Return of Benchmark Portfolio: {cum_ret_bm_out}")
#     print(f"Cumulative Return of Manual Strategy Portfolio: {cum_ret_out}")
#     print()
#     print(f"Standard Deviation of Benchmark Portfolio: {std_daily_ret_bm_out}")
#     print(f"Standard Deviation of Manual Strategy Portfolio: {std_daily_ret_out}")
#     print()
#     print(f"Average Daily Return of Benchmark Portfolio: {avg_daily_ret_bm_out}")
#     print(f"Average Daily Return of Manual Strategy Portfolio: {avg_daily_ret_out}")
#     print()
#     print(f"Final Portfolio Value: {portvals_out.iloc[-1, 0]}")
#
#     # Plot out-of-sample chart
#     fig, ax = plt.subplots()
#     bm_out.plot(ax=ax, color="green")
#     portvals_out.plot(ax=ax, color="red")
#     plt.legend(["Benchmark", "Manual Strategy"])
#     plt.title("Manual Strategy vs. Benchmark (Out-of-Sample)")
#     plt.xlabel("Date")
#     plt.ylabel("Normalized Value")
#     plt.grid()
#     plt.tight_layout()
#     plt.savefig("6.Comparision_out.png")
#
#
# if __name__ == "__main__":
#     test_code()