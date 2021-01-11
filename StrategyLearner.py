import datetime as dt		  	 		  		  		    	 		 		   		 		  
import pandas as pd
import numpy as np
import util as ut
from indicators import get_indicators
import QLearner as ql

  		   	  			  	 		  		  		    	 		 		   		 		  
class StrategyLearner(object):

    def author(self):
        return ""
  		   	  			  	 		  		  		    	 		 		   		 		  
    # constructor  		   	  			  	 		  		  		    	 		 		   		 		  
    def __init__(self, verbose = False, impact=0.0, commission=0.0, min_iter=15, max_iter=100):
        self.verbose = verbose  		   	  			  	 		  		  		    	 		 		   		 		  
        self.impact = impact
        self.commission = commission
        self.min_iter = min_iter
        self.max_iter = max_iter
        self.num_bins = 10
        self.num_states = self.num_bins ** 3


    def get_stock_data(self, symbol, dates):
        data = ut.get_data([symbol], dates)
        prices = data[symbol]
        prices /= prices.iloc[0]
        indices = data["SPY"]
        indices /= indices.iloc[0]
        trading_days = indices.index
        return prices, trading_days

    def discretize(self, x, indicators):
        _, x_bins = pd.qcut(x, self.num_bins, retbins=True, labels=False)
        x_indices = np.clip(np.digitize(x, x_bins, right=True) - 1, 0, self.num_bins - 1)
        x_indices = pd.Series(x_indices, index=indicators.index)
        return x_indices

    def get_discretized_states(self, prices, symbol):

        # Get indicators
        indicators = get_indicators(prices.to_frame(symbol))
        sma_ratio = indicators["Price/SMA"]
        bb_ratio = indicators["BB Value"]
        momentum = indicators["Momentum"]
        df_indicators = pd.DataFrame(index=indicators.index)

        # Discretize the indicators for discretized states of in-sample data
        bb_ratio_indices = self.discretize(bb_ratio, indicators)
        sma_ratio_indices = self.discretize(sma_ratio, indicators)
        momentum_indices = self.discretize(momentum, indicators)
        df_indicators["State"] = (bb_ratio_indices.astype(str) + sma_ratio_indices.astype(str) + momentum_indices.astype(str)).astype(np.int)
        return df_indicators["State"]

    # this method should create a QLearner, and train it for trading
    def addEvidence(self, symbol="IBM", sd=dt.datetime(2008, 1, 1), ed=dt.datetime(2009, 1, 1), sv=10000):

        # Fetch in-sample data
        prices, trading_days = self.get_stock_data(symbol, pd.date_range(sd, ed))
        daily_returns = (prices / prices.shift(1)) - 1

        self.learner = ql.QLearner(
            num_states=self.num_states,
            num_actions=3,
            alpha=0.2,
            gamma=0.9,
            rar=0.5,
            radr=0.99,
            dyna=0,
            verbose=self.verbose,
        )

        # Training the learner
        i = 0
        converged = False
        df_trades_previous = None
        states = self.get_discretized_states(prices, symbol)
        while (i <= self.max_iter and not converged) or (i <= self.min_iter):

            # first day
            action = self.learner.querysetstate(states.iloc[0])
            holdings = 0
            df_trades = pd.Series(index=states.index)

            for day, state in states.iteritems():

                reward = holdings * daily_returns.loc[day]
                if action == 0 or action == 1:
                    reward *= (1 - self.impact)

                action = self.learner.query(state, reward)

                # SHORT
                if action == 0:
                    df_trades.loc[day] = {-1000: 0, 0: -1000, 1000: -2000,}.get(holdings)
                # LONG
                elif action == 1:
                    df_trades.loc[day] = {-1000: 2000, 0: 1000, 1000: 0,}.get(holdings)
                # DO NOTHING
                elif action == 2:
                    df_trades.loc[day] = 0

                holdings += df_trades.loc[day]

            if (df_trades_previous is not None) and (df_trades.equals(df_trades_previous)):
                converged = True

            df_trades_previous = df_trades
            i += 1

    def testPolicy(self, symbol="IBM", sd=dt.datetime(2009, 1, 1), ed=dt.datetime(2010, 1, 1), sv=10000):

        # Fetch out-of-sample data
        prices, trading_days = self.get_stock_data(symbol, pd.date_range(sd, ed))

        holdings = 0
        states = self.get_discretized_states(prices, symbol)
        df_trades = pd.Series(index=states.index)

        for day, state in states.iteritems():
            action = self.learner.querysetstate(state)

            # SHORT
            if action == 0:
                df_trades.loc[day] = {-1000: 0, 0: -1000, 1000: -2000,}.get(holdings)
            # LONG
            elif action == 1:
                df_trades.loc[day] = {-1000: 2000, 0: 1000, 1000: 0,}.get(holdings)
            # DO NOTHING
            elif action == 2:
                df_trades.loc[day] = 0

            holdings += df_trades.loc[day]

        return df_trades.to_frame(symbol)
  		   	  			  	 		  		  		    	 		 		   		 		  

  		   	  			  	 		  		  		    	 		 		   		 		  
    #     # example usage of the old backward compatible util function
    #     syms=[symbol]
    #     dates = pd.date_range(sd, ed)
    #     prices_all = ut.get_data(syms, dates)  # automatically adds SPY
    #     prices = prices_all[syms]  # only portfolio symbols
    #     prices_SPY = prices_all['SPY']  # only SPY, for comparison later
    #     if self.verbose: print(prices)
  	#
    #     # example use with new colname
    #     volume_all = ut.get_data(syms, dates, colname = "Volume")  # automatically adds SPY
    #     volume = volume_all[syms]  # only portfolio symbols
    #     volume_SPY = volume_all['SPY']  # only SPY, for comparison later
    #     if self.verbose: print(volume)
  	#
    # # this method should use the existing policy and test it against new data
    # def testPolicy(self, symbol = "IBM", \
    #     sd=dt.datetime(2009,1,1), \
    #     ed=dt.datetime(2010,1,1), \
    #     sv = 10000):
  	#
    #     # here we build a fake set of trades
    #     # your code should return the same sort of data
    #     dates = pd.date_range(sd, ed)
    #     prices_all = ut.get_data([symbol], dates)  # automatically adds SPY
    #     trades = prices_all[[symbol,]]  # only portfolio symbols
    #     trades_SPY = prices_all['SPY']  # only SPY, for comparison later
    #     trades.values[:,:] = 0 # set them all to nothing
    #     trades.values[0,:] = 1000 # add a BUY at the start
    #     trades.values[40,:] = -1000 # add a SELL
    #     trades.values[41,:] = 1000 # add a BUY
    #     trades.values[60,:] = -2000 # go short from long
    #     trades.values[61,:] = 2000 # go long from short
    #     trades.values[-1,:] = -1000 #exit on the last day
    #     if self.verbose: print(type(trades)) # it better be a DataFrame!
    #     if self.verbose: print(trades)
    #     if self.verbose: print(prices_all)
    #     return trades



# if __name__=="__main__":
#     print("One does not simply think up a strategy")

