import sys

import numpy as np

if __name__ == '__main__':
    lower_bound = int(sys.argv[1])
    upper_bound = int(sys.argv[2])
    print(np.random.randint(lower_bound, upper_bound))
