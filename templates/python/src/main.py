import sys

import numpy as np

if __name__ == "__main__":
    """
    Example program: reads CLI arguments, converts them to integers,
    then outputs a random integer between both input values
    """
    lower_bound = int(sys.argv[1])
    upper_bound = int(sys.argv[2])
    print(np.random.randint(lower_bound, upper_bound))
