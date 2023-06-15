import numpy as np


class General:

    def __init__(self) -> None:
        pass

    def binomt(self, numP, u, d, S0):
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
        print('-----binom-lattice-----')
        for now in arr:
            print(now)

    def backtr(self, arr, pos, rec, p):

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

    def option(self, arr, K, type, u, d, r, t):

        def payoffs():
            now = arr[-1]

            def func_put(S):
                return max(K - S, 0)

            def func_call(S):
                return max(S - K, 0)

            func = func_call if type == 'c' else func_put

            buffer = []
            for s in now:
                buffer.append(
                    func(s)
                )
            return buffer

        def backprop(cp_tree, u, d, R):

            if len(cp_tree) == 1:
                return

            lst = []
            now = cp_tree[-1]
            for i in range(len(now) - 1, 2):
                lst.append(
                    R**-1 * ((R - d) / (u - d) *
                             now[i] + (u - R) / (u - d) * now[i + 1])
                )
                cp_tree[-2] = lst
                backprop(cp_tree[:-1], u, d, R)
                return cp_tree

        cp_tree = []
        for a in arr[:-1]:
            layer = []
            cp_tree.append(layer)
            for e in a:
                layer.append(None)
        cp_tree.append(
            payoffs()
        )
        R = np.e**(r*t)
        backprop(cp_tree, u, d, R)
