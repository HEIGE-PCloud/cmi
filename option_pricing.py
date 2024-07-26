import numpy as np
import time
from black_scholes import call_value, call_delta, put_value, put_delta
from cards import Cards
import statistics


def call_payoff(underlying, strike):
    return np.maximum(underlying - strike, 0)


def put_payoff(underlying, strike):
    return np.maximum(strike - underlying, 0)


def option_pricing(call_strike: float, put_strike: float, cards: Cards):
    remaining_cards = np.array(cards.get_remaining_cards())
    cnt = 100000

    # Generate a matrix of shuffled cards
    shuffled_cards = np.array(
        [np.random.permutation(remaining_cards) for _ in range(cnt)]
    )

    # Sum the first 20 elements of each shuffle
    sums = (
        shuffled_cards[:, : cards.get_remaining_cards_to_choose()].sum(axis=1)
        + cards.get_chosen_cards_sum()
    )

    # Calculate call and put values
    call_totals = call_payoff(sums, call_strike)
    put_totals = put_payoff(sums, put_strike)

    # Average the totals
    call_price = call_totals.mean()
    put_price = put_totals.mean()
    return call_price, put_price


def get_call_vol(cards: Cards, strike: float, iterations: int = 30):
    vol_low = 0.0001
    vol_high = 1.0
    underlying_price = cards.get_theoretical_price()
    remaining_cards_to_choose = cards.get_remaining_cards_to_choose()
    for _ in range(iterations):
        vol_mid = (vol_low + vol_high) / 2.0
        res = call_value(
            underlying_price,
            strike,
            remaining_cards_to_choose,
            0.0,
            vol_mid,
        )
        if res > call_price:
            vol_high = vol_mid
        else:
            vol_low = vol_mid
    return vol_low


def get_put_vol(cards: Cards, strike: float, iterations: int = 30):
    vol_low = 0.0001
    vol_high = 1.0
    underlying_price = cards.get_theoretical_price()
    remaining_cards_to_choose = cards.get_remaining_cards_to_choose()
    for _ in range(iterations):
        vol_mid = (vol_low + vol_high) / 2.0
        res = put_value(
            underlying_price,
            strike,
            remaining_cards_to_choose,
            0.0,
            vol_mid,
        )
        if res > call_price:
            vol_high = vol_mid
        else:
            vol_low = vol_mid
    return vol_low

if __name__ == "__main__":
    start_time = time.time()

    cards = Cards()
    call_price, put_price = option_pricing(150, 130, cards)
    call_vol = get_call_vol(cards, 150)
    put_vol = get_put_vol(cards, 130)
    print("Theo: ", cards.get_theoretical_price())
    print("150 Call: ", call_price)
    print(
        "Estimated 150 Call:",
        call_value(
            cards.get_theoretical_price(),
            150,
            cards.get_remaining_cards_to_choose(),
            0,
            call_vol,
        ),
    )

    print("130 Put:", put_price)
    print(
        "Estimated 130 Put:",
        put_value(
            cards.get_theoretical_price(),
            130,
            cards.get_remaining_cards_to_choose(),
            0,
            put_vol,
        ),
    )

    print("Call Volatility:", call_vol)

    print("Put Volatility:", put_vol)
    print(
        "Call Delta:",
        call_delta(
            cards.get_theoretical_price(),
            150,
            cards.get_remaining_cards_to_choose(),
            0,
            call_vol,
        ),
    )
    print(
        "Put Delta:",
        put_delta(
            cards.get_theoretical_price(),
            130,
            cards.get_remaining_cards_to_choose(),
            0,
            put_vol,
        ),
    )
    end_time = time.time()
    print("Time taken:", end_time - start_time, "seconds")
