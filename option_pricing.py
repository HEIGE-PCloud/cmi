import numpy as np
import time
from black_scholes import call_value, call_delta, put_value, put_delta

all_cards = [
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
]

chosen_cards = []

total_cards_to_choose = 20
remaining_cards_to_choose = total_cards_to_choose - len(chosen_cards)
remaining_cards = all_cards.copy()
for x in chosen_cards:
    remaining_cards.remove(x)

cards = np.array(remaining_cards)
ev = np.mean(cards)
chosen_cards_sum = sum(chosen_cards)
theo_price = chosen_cards_sum + ev * remaining_cards_to_choose


def call_payoff(underlying, strike):
    return np.maximum(underlying - strike, 0)

def put_payoff(underlying, strike):
    return np.maximum(strike - underlying, 0)


start_time = time.time()

cnt = 100000

# Generate a matrix of shuffled cards
shuffled_cards = np.array([np.random.permutation(cards) for _ in range(cnt)])

# Sum the first 20 elements of each shuffle
sums = shuffled_cards[:, :remaining_cards_to_choose].sum(axis=1) + chosen_cards_sum

# Calculate call and put values
call_totals = call_payoff(sums, 150)
put_totals = put_payoff(sums, 130)

# Average the totals
call_price = call_totals.mean()
put_price = put_totals.mean()

vol_low = 0.0001
vol_high = 1.0
for _ in range(30):
    vol_mid = (vol_low + vol_high) / 2
    res = call_value(theo_price, 150, remaining_cards_to_choose, 0, vol_mid)
    if res > call_price:
        vol_high = vol_mid
    else:
        vol_low = vol_mid

print("Theo: ", theo_price)
print("150 Call: ", call_price)
print("130 Put:", put_price)
print("Volatility:", vol_low)
print("Estimated 150 Call:", call_value(theo_price, 150, remaining_cards_to_choose, 0, vol_low))
print("Call Delta:", call_delta(theo_price, 150, remaining_cards_to_choose, 0, vol_low))
vol_low = 0.0001
vol_high = 1.0
for _ in range(30):
    vol_mid = (vol_low + vol_high) / 2
    res = put_value(theo_price, 130, remaining_cards_to_choose, 0, vol_mid)
    if res > call_price:
        vol_high = vol_mid
    else:
        vol_low = vol_mid
print("Volatility:", vol_low)
print("Estimated 130 Put:", put_value(theo_price, 130, remaining_cards_to_choose, 0, vol_low))
print("Put Delta:", put_delta(theo_price, 130, remaining_cards_to_choose, 0, vol_low))
end_time = time.time()
print("Time taken:", end_time - start_time, "seconds")
