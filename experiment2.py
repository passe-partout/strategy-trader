import numpy as np
import pandas as pd
import datetime as dt
import StrategyLearner as sl
from matplotlib import pyplot as plt
from util import get_data
from marketsimcode import compute_portvals
from ManualStrategy import ManualStrategy


def author():
    return ""


def cum_ret(portvals):
    cum_ret = (portvals / portvals.iloc[0,0]) - 1
    return cum_ret.iloc[-1,0]

def sharpe_ratio(portvals):
    daily_ret = (portvals / portvals.shift(1)) - 1
    avg_daily_ret = daily_ret.iloc[1:, 0].mean()
    std_daily_ret = daily_ret.iloc[1:, 0].std()
    return np.sqrt(252) * avg_daily_ret / std_daily_ret

def experiment_2():

    symbol = "JPM"
    sv = 100000
    commission = 0.0
    in_sample_sd = dt.datetime(2008, 1, 1)
    in_sample_ed = dt.datetime(2009, 12, 31)
    trading_days = get_data(["SPY"], dates=pd.date_range(in_sample_sd, in_sample_ed)).index

    df_cum_ret = pd.DataFrame(columns=["Benchmark", "Manual Strategy", "QLearning Strategy"], index=np.linspace(0.0, 0.01, num=15))
    df_sharpe_ratio = pd.DataFrame(columns=["Benchmark", "Manual Strategy", "QLearning Strategy"], index=np.linspace(0.0, 0.01, num=15))

    for impact, _ in df_cum_ret.iterrows():

        # Compute portvals of benchmark
        bm_trade = pd.DataFrame([1000] + [0] * (len(trading_days) - 1), columns=[symbol], index=trading_days)
        portvals_bm = compute_portvals(bm_trade, start_val=sv, commission=commission, impact=impact)
        df_cum_ret.loc[impact, "Benchmark"] = cum_ret(portvals_bm)
        df_sharpe_ratio.loc[impact, "Benchmark"] = sharpe_ratio(portvals_bm)

        # Compute portvals of manual strategy
        ms = ManualStrategy()
        df_trades_ms = ms.testPolicy(symbol=symbol, sd=in_sample_sd, ed=in_sample_ed, sv=sv)
        portvals_ms = compute_portvals(df_trades_ms, start_val=sv, commission=commission, impact=impact)
        df_cum_ret.loc[impact, "Manual Strategy"] = cum_ret(portvals_ms)
        df_sharpe_ratio.loc[impact, "Manual Strategy"] = sharpe_ratio(portvals_ms)

        # Compute portvals of QLearning strategy
        learner = sl.StrategyLearner(verbose=False, impact=impact, commission=commission)
        learner.addEvidence(symbol=symbol, sd=in_sample_sd, ed=in_sample_ed, sv=sv)
        df_trades_ql = learner.testPolicy(symbol=symbol, sd=in_sample_sd, ed=in_sample_ed, sv=sv)
        portvals_ql = compute_portvals(df_trades_ql, start_val=sv, commission=commission, impact=impact)
        df_cum_ret.loc[impact, "Strategy QLearner"] = cum_ret(portvals_ql)
        df_sharpe_ratio.loc[impact, "Strategy QLearner"] = sharpe_ratio(portvals_ql)

    # Plot in-sample results
    fig, ax = plt.subplots()
    df_cum_ret[["Benchmark"]].plot(ax=ax, color="green", marker="o")
    df_cum_ret[["Manual Strategy"]].plot(ax=ax, color="red", marker="o")
    df_cum_ret[["Strategy QLearner"]].plot(ax=ax, color="blue", marker="o")
    plt.title("In-sample Cumulative Return In Relation to Impact on JPM")
    plt.xlabel("Impact")
    plt.ylabel("Cumulative Return")
    plt.grid()
    plt.tight_layout()
    plt.savefig("2.Cum_ret_impact_in_sample.png")

    fig, ax = plt.subplots()
    df_sharpe_ratio[["Benchmark"]].plot(ax=ax, color="green", marker="s")
    df_sharpe_ratio[["Manual Strategy"]].plot(ax=ax, color="red", marker="s")
    df_sharpe_ratio[["Strategy QLearner"]].plot(ax=ax, color="blue", marker="s")
    plt.title("In-sample Sharpe Ratio In Relation to Impact on JPM")
    plt.xlabel("Impact")
    plt.ylabel("Sharpe Ratio")
    plt.grid()
    plt.tight_layout()
    plt.savefig("3.Sharpe_ratio_impact_in_sample.png")


if __name__ == "__main__":
    experiment_2()