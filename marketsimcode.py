import pandas as pd
from util import get_data
from datetime import datetime

def author():
    return ''

# accepting a "trades" data frame
def compute_portvals(df_trades, start_val=1000000, commission=9.95, impact=0.005):

    df_trades = df_trades.sort_index()
    sd = df_trades.index[0]
    ed = df_trades.index[-1]

    symbols = df_trades.columns.unique().tolist()
    prices = {}
    for symbol in symbols:
        prices[symbol] = get_data([symbol], pd.date_range(sd, ed), colname='Adj Close')
        prices[symbol] = prices[symbol].fillna(method="ffill")
        prices[symbol] = prices[symbol].fillna(method="bfill")

    # List the trading days
    trading_days_SPY = get_data(['SPY'], pd.date_range(sd, ed))
    trading_days = pd.date_range(sd, ed)
    for d in trading_days:
        if d not in trading_days_SPY.index:
            trading_days = trading_days.drop(d)

    portvals = pd.DataFrame(index=trading_days, columns=["PortVal"] + symbols)

    holdings = start_val
    today = None
    for next_day in trading_days:

        # Copy previous trading day's portfolio state
        if today is not None:
            portvals.loc[next_day, :] = portvals.loc[today, :]
            portvals.loc[next_day, "PortVal"] = 0
        else:
            portvals.loc[next_day, :] = 0

        # Execute orders
        if next_day in df_trades.index:
            current_orders = df_trades.loc[[next_day]]
            for symbol in current_orders.columns:
                order = current_orders.iloc[0].loc[symbol]
                shares = abs(order)
                price = prices[symbol].loc[next_day, symbol]

                if order > 0:  # BUY
                    price = (1 + impact) * price
                    holdings -= (price * shares + commission)
                    portvals.loc[next_day, symbol] += shares
                elif order < 0:  # SELL
                    price = (1 - impact) * price
                    holdings += (price * shares - commission)
                    portvals.loc[next_day, symbol] -= shares

        for symbol in symbols:
            price = prices[symbol].loc[next_day, symbol]
            portvals.loc[next_day, "PortVal"] += portvals.loc[next_day, symbol] * price + holdings

        today = next_day

    # Remove empty lines and normalize final portvals
    portvals = portvals.sort_index().iloc[:, 0].to_frame()
    portvals /= portvals.iloc[0, :]
    return portvals


# def test_code():
#
#     df_trades = pd.DataFrame([-1000, 1000, 0], columns=["JPM"], index=pd.date_range(datetime(2008, 1, 7), datetime(2008, 1, 9)))
#     print(compute_portvals(df_trades))

    # of = "./orders/orders-01.csv"
    # of = "./orders/orders-02.csv"
    # for i in range(1, 13):
    #     if i < 10:
    #         of = "./orders/orders-0" + str(i) + ".csv"
    #     else:
    #         of = "./orders/orders-" + str(i) + ".csv"
    #
    #     portvals = compute_portvals(orders_file=of, start_val=sv)
    #
    #     if isinstance(portvals, pd.DataFrame):
    #         portvals = portvals[portvals.columns[0]]  # just get the first column
    #     else:
    #         "warning, code did not return a DataFrame"

        # start_date = portvals.index.min()
        # end_date = portvals.index.max()
        # cum_ret = (portvals[-1] / portvals[0]) - 1
        # daily_ret = (portvals / portvals.shift(1)) - 1
        # avg_daily_ret = daily_ret[1:].mean()
        # std_daily_ret = daily_ret[1:].std()
        # sharpe_ratio = np.sqrt(252) * avg_daily_ret / std_daily_ret
        #
        # SPY = get_data(['$SPX'], pd.date_range(start_date, end_date))
        # cum_ret_SPY = SPY.iloc[-1, 1] / SPY.iloc[0, 1] - 1
        # daily_ret_SPY = SPY.iloc[:, 1] / SPY.iloc[:, 1].shift(1) - 1
        # avg_daily_ret_SPY = daily_ret_SPY[1:].mean()
        # std_daily_ret_SPY = daily_ret_SPY[1:].std()
        # sharpe_ratio_SPY = np.sqrt(252) * avg_daily_ret_SPY / std_daily_ret_SPY
        #
        # print("**************************" + of[9:] + "**************************")
        # print()
        # print("Date Range: {start_date} to {end_date}")
        # print()
        # print("Sharpe Ratio of Fund: {sharpe_ratio}")
        # print("Sharpe Ratio of SPY : {sharpe_ratio_SPY}")
        # print()
        # print("Cumulative Return of Fund: {cum_ret}")
        # print("Cumulative Return of SPY : {cum_ret_SPY}")
        # print()
        # print("Standard Deviation of Fund: {std_daily_ret}")
        # print("Standard Deviation of SPY : {std_daily_ret_SPY}")
        # print()
        # print("Average Daily Return of Fund: {avg_daily_ret}")
        # print("Average Daily Return of SPY : {avg_daily_ret_SPY}")
        # print()
        # print("Final Portfolio Value: {portvals[-1]}")
        # print()


# if __name__ == "__main__":
#     test_code()
