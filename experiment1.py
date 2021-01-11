import pandas as pd
import datetime as dt
import StrategyLearner as sl
from matplotlib import pyplot as plt
from util import get_data
from marketsimcode import compute_portvals
from ManualStrategy import ManualStrategy


def author():
    return ""


def experiment_1():

    symbol = "JPM"
    sv = 100000
    commission = 0.0
    impact = 0.005
    in_sample_sd = dt.datetime(2008, 1, 1)
    in_sample_ed = dt.datetime(2009, 12, 31)
    trading_days = get_data(["SPY"], pd.date_range(in_sample_sd, in_sample_ed)).index

    # Compute portvals of benchmark
    bm_trade = pd.DataFrame([1000] + [0] * (len(trading_days) - 1), columns=[symbol], index=trading_days)
    portvals_bm = compute_portvals(bm_trade, start_val=sv, commission=commission, impact=impact)

    # Compute portvals of manual strategy
    ms = ManualStrategy()
    df_trades_ms = ms.testPolicy(symbol=symbol, sd=in_sample_sd, ed=in_sample_ed, sv=sv)
    portvals_ms = compute_portvals(df_trades_ms, start_val=sv, commission=commission, impact=impact)

    # Compute portvals of QLearning strategy
    learner = sl.StrategyLearner(verbose=False, impact=impact, commission=commission)
    learner.addEvidence(symbol=symbol, sd=in_sample_sd, ed=in_sample_ed, sv=sv)
    df_trades_ql = learner.testPolicy(symbol=symbol, sd=in_sample_sd, ed=in_sample_ed, sv=sv)
    portvals_ql = compute_portvals(df_trades_ql, start_val=sv, commission=commission, impact=impact)

    # Plot in-sample comparison
    fig, ax = plt.subplots()
    portvals_bm.plot(ax=ax, color="green")
    portvals_ms.plot(ax=ax, color="red")
    portvals_ql.plot(ax=ax, color="blue")
    plt.legend(["Benchmark", "Manual Strategy", "Strategy QLearner"])
    plt.title("Experiment 1:  In-sample Comparison on JPM")
    plt.xlabel("Date")
    plt.ylabel("Normalized Portfolio Value")
    plt.grid()
    plt.tight_layout()
    plt.savefig("1.Comparison_in_sample.png")


if __name__ == "__main__":
    experiment_1()