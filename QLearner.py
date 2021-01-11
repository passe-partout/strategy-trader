import numpy as np
import random as rand

class QLearner(object):

    def author(self):
        return ''

    def __init__(self, \
        num_states=100, \
        num_actions = 4, \
        alpha = 0.2, \
        gamma = 0.9, \
        rar = 0.5, \
        radr = 0.99, \
        dyna = 0, \
        verbose = False):

        self.num_states = num_states
        self.num_actions = num_actions
        self.alpha = alpha
        self.gamma = gamma
        self.rar = rar
        self.radr = radr
        self.dyna = dyna
        self.verbose = verbose
        self.s = 0
        self.a = 0
        self.Q = np.zeros((num_states, num_actions))
        np.random.seed(100)
        rand.seed(100)

        if dyna > 0:
            self.T = np.zeros((num_states, num_actions, num_states))
            self.R = np.zeros((num_states, num_actions))
            self.Tc = np.full((num_states, num_actions, num_states), 0.00001)

    def querysetstate(self, s):
        """  		   	  			  	 		  		  		    	 		 		   		 		  
        @summary: Update the state without updating the Q-table  		   	  			  	 		  		  		    	 		 		   		 		  
        @param s: The new state  		   	  			  	 		  		  		    	 		 		   		 		  
        @returns: The selected action  		   	  			  	 		  		  		    	 		 		   		 		  
        """
        # take a random action
        if np.random.uniform() < self.rar:
            action = rand.randint(0, self.num_actions-1)
        # OR consult Q table for an action
        else:
            action = self.Q[s, :].argmax()

        self.s = s
        self.a = action
        if self.verbose: print(f"s = {s}, a = {action}")
        return action

    def query(self,s_prime,r):
        """  		   	  			  	 		  		  		    	 		 		   		 		  
        @summary: Update the Q table and return an action  		   	  			  	 		  		  		    	 		 		   		 		  
        @param s_prime: The new state  		   	  			  	 		  		  		    	 		 		   		 		  
        @param r: The ne state  		   	  			  	 		  		  		    	 		 		   		 		  
        @returns: The selected action  		   	  			  	 		  		  		    	 		 		   		 		  
        """
        # update Q table with new input
        self.update_Q(self.s, self.a, s_prime, r)

        # execute Dyna
        if self.dyna > 0:
            self.run_dyna(s_prime,r)

        # new action to take
        action = self.querysetstate(s_prime)
        # action = rand.randint(0, self.num_actions-1)

        # update rar according to radr
        self.rar *= self.radr

        if self.verbose: print(f"s = {s_prime}, a = {action}, r={r}")
        return action

    def update_Q(self,s,a,s_prime,r, axis=0):
        self.Q[s,a] = (1-self.alpha) * self.Q[s,a] + self.alpha * (r + self.gamma * self.Q[s_prime, self.Q[s_prime, :].argmax(axis=axis)])

    def run_dyna(self,s_prime,r):

        # update model
        self.Tc[self.s, self.a, s_prime] += 1
        self.T[self.s, self.a, :] = self.Tc[self.s, self.a, :] / self.Tc[self.s, self.a, :].sum()
        self.R[self.s, self.a] = (1-self.alpha) * self.R[self.s, self.a] + self.alpha * r

        # hallucinate and update Q table
        rand_s = np.random.randint(0, self.num_states, size=self.dyna)
        rand_a = np.random.randint(0, self.num_actions, size=self.dyna)
        d_s_prime = self.T[rand_s, rand_a, :].argmax(axis=1)
        d_r = self.R[rand_s, rand_a]
        self.update_Q(rand_s, rand_a, d_s_prime, d_r, axis=1)


if __name__=="__main__":  		   	  			  	 		  		  		    	 		 		   		 		  
    print("Remember Q from Star Trek? Well, this isn't him")  		   	  			  	 		  		  		    	 		 		   		 		  
