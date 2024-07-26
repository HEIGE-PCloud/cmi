import numpy as np
import time
cards = np.array([
    1.0, 1.0, 1.0, 1.0,
    2.0, 2.0, 2.0, 2.0,
    3.0, 3.0, 3.0, 3.0,
    4.0, 4.0, 4.0, 4.0,
    5.0, 5.0, 5.0, 5.0,
    6.0, 6.0, 6.0, 6.0,
    7.0, 7.0, 7.0, 7.0,
    8.0, 8.0, 8.0, 8.0,
    9.0, 9.0, 9.0, 9.0,
    10.0, 10.0, 10.0, 10.0,
    11.0, 11.0, 11.0, 11.0,
    12.0, 12.0, 12.0, 12.0,
    13.0, 13.0, 13.0, 13.0
])


def call_value(underlying, strike):
    return np.maximum(underlying - strike, 0)

def put_value(underlying, strike):
    return np.maximum(strike - underlying, 0)


start_time = time.time()

cnt = 100000

# Generate a matrix of shuffled cards
shuffled_cards = np.array([np.random.permutation(cards) for _ in range(cnt)])

# Sum the first 20 elements of each shuffle
sums = shuffled_cards[:, :20].sum(axis=1)

# Calculate call and put values
call_totals = call_value(sums, 150)
put_totals = put_value(sums, 130)

# Average the totals
call_price = call_totals.mean()
put_price = put_totals.mean()


end_time = time.time()
print("Time taken:", end_time - start_time, "seconds")

print(call_price)
print(put_price)
