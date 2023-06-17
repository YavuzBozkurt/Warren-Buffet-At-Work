import numpy as np


class General:
    """
    this is a class for general purpose method implementations
    to solve problems. Create an instance of this class to use
    the methods.
    """

    def __init__(self) -> None:
        """
        this is the empty constructor of the class,
        nothing to fetch
        """
        pass

    def binomt(self, numP, u, d, S0):
        """
        this is the method to construct a binomial 
        lattice tree, as parameter, it gets
        `self` instance itself
        `numP` number of periods in the model
        `u` up factor of the tree
        `d` down factor of the tre
        `S0` initial stock price
        """
        # inititalize the tree
        whole = [
            [S0]
        ]
        t = 1
        # as long as periods to go
        while t <= numP:
            # get the current period
            now = whole[-1]
            # ready the next period
            nxt = []
            # per projection in today
            # there are two projections,
            # namely, up or down
            for i in range(len(now)):
                # up
                nxt.append(
                    now[i] * u
                )
                # down
                nxt.append(
                    now[i] * d
                )
            # projections for next period are done,
            # add them to the tree
            whole.append(nxt)
            # go to next period
            t += 1
        # return the complete tree
        return whole

    def bindomrender(self, arr):
        """
        this is the method to render a computed
        binomial lattice tree for visualization
        sake, as parameter, it gets
        `self` instance itself
        `arr` the binomial lattice tree
        """
        print('-----binom-lattice-----')
        for now in arr:
            # display per row in seperate line
            print(now)

    def backtr(self, arr, pos, rec, p):
        """
        this is the backtracking method to compute
        the expected price of a stock, as parameter,
        it gets
        `self` instance itself
        `arr` binomial lattice tree
        `pos` an index to select candidates with
        `rec` an array  to store all results and paths
        `p` probability of having up factor in the stock
        """
        # Base case
        if pos == len(arr) - 1:
            # add a copy of the path
            # compute probability of the path
            rec.append(
                ([e for e in arr], p**sum(arr) * (1 - p)**(len(arr) - sum(arr)))
            )
            # give the updated path to the ancestor call
            return rec

        # per candidate (1 ~ p, 0 ~ (1 - p))
        for el in [1, 0]:
            # select
            arr[pos + 1] = el
            # call
            rec = backtr(self, arr, pos + 1, rec, p)
            # backtrack
            arr[pos + 1] = ''

        # return all paths and probabilties
        return rec

    def option(self, arr, K, typ: str, u, d, r, t):
        """
        this is the method to compute option (call / put) prices
        as parameter, it gets
        `self` instance itself
        `arr` the binomial lattice tree
        `K` strike price of the option
        `typ` the type of the option (call ~ c, put ~ p)
        `u` up factor of the tree
        `d` down factor of the tree
        `r` risk free interest rate 
        `t` Δt 
        """

        def payoffs():
            """
            this is the method that computes the expected
            non-discounted option payoffs, so full option
            payoffs
            """
            # get the final stock prices
            now = arr[-1]
            # select the appropriate payoff function
            func = self.func_call if typ == 'c' else self.func_put
            # set buffer where payoffs are to be stored
            buffer = []
            for s in now:
                buffer.append(
                    func(s, K)
                )
            return buffer

        def backprop(cp_tree, l, u, d, R):
            """
            this is a method that implements the
            backpropogating / backword recursing
            for option price computation,
            as parameter, it gets
            `cp_tree` the option binomial lattice tree
            `l` an index to track layers of the binomial 
            lattic tree
            `u` up factor of the tree
            `d` down factor of the tree
            `R` discount factor (continuous compounding)
            """
            # Base case
            if len(cp_tree[l]) == 1:
                # forward the current cp_tree
                # to the ancestor call
                return cp_tree

            # set fresh empty list where new option prices
            # will be stored
            lst = []
            # get the last layer of option binomial lattice
            now = cp_tree[l]
            for i in range(0, len(now) - 1, 2):
                lst.append(
                    # apply the recursive formula to compute the
                    # new discounted expected payoff
                    R**-1 * ((R - d) / (u - d) *
                             now[i] + (u - R) / (u - d) * now[i + 1])
                )
            # fetch the newly computed layer to the previous layer
            # of the binomial tree
            cp_tree[l-1] = lst
            # do backpropogation
            cp_tree = backprop(cp_tree, l-1, u, d, R)
            # return the whole option binomial lattice tree
            return cp_tree

        typ = typ.lower()
        assert typ == 'c' or typ == 'p'
        # initialize the option binomial lattice tree
        cp_tree = []
        # get all layers except the last one
        for a in arr[:-1]:
            layer = []
            # add the layer to the option tree
            cp_tree.append(layer)
            # per element in the stock binomial lattice
            # tree, add a None to the new layer
            # (None representing a node with no value)
            for e in a:
                layer.append(None)
        # add the payoff layer to the end
        cp_tree.append(
            payoffs()
        )
        # compute the yearly discount
        R = np.e**(r*t)
        # start backpropogation
        cp_tree = backprop(cp_tree, len(cp_tree)-1,  u, d, R)
        # return the result of backpropogation
        return cp_tree

    def america_option(self, arr, cp_tree, typ, K):
        """
        this is a method that computes the price of a
        american option
        as parameter it gets
        `self` instance itself
        `arr` binomial tree for stock prices
        `cp_tree` binomial tree for a european option prices
        `typ` type of the option (call ~ c, put ~ p)
        `K` the strike price of the option
        """
        acp_tree = []
        func = self.func_call if typ == 'c' else self.func_put
        for i in range(len(cp_tree)):
            new = []
            acp_tree.append(new)
            for j in range(len(cp_tree[i])):
                new.append(
                    (func(arr[i][j], K), cp_tree[i][j])
                )
        return acp_tree

    def func_put(self, S, K):
        """
        auxiliary
        this is the payoff for a put option
        as parameter, it gets
        `S` stock price
        """
        return max(K - S, 0)

    def func_call(self, S, K):
        """
        auxiliary
        this is the payoff for a call option
        as parameter, it gets
        `S` stock price
        """
        return max(S - K, 0)
