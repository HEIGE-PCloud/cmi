import numpy as np
import time
from cards import Cards
import statistics
import subprocess


def call_payoff(underlying, strike):
    return np.maximum(underlying - strike, 0)


def put_payoff(underlying, strike):
    return np.maximum(strike - underlying, 0)


def option_pricing(
    call_strike: float, put_strike: float, cards: Cards, iterations: int = 100000
):
    remaining_cards = np.array(cards.get_remaining_cards())

    # Generate a matrix of shuffled cards
    shuffled_cards = np.apply_along_axis(
        np.random.permutation, 1, np.tile(remaining_cards, (iterations, 1))
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


def option_pricing_cpp(cards: Cards, threads: int = 4, iterations: int = 300000):
    with subprocess.Popen(
        ["./a.out", str(threads), str(iterations)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
    ) as process:
        input_data = str(cards.get_chosen_cards_num()) + "\n"
        input_data += " ".join(map(str, cards._chosen_cards)) + "\n"
        output, errors = process.communicate(input=input_data)
        lines = output.split("\n")
        call_price = float(lines[0])
        put_price = float(lines[1])
        call_delta = float(lines[2])
        put_delta = float(lines[3])
        return call_price, put_price, call_delta, put_delta


def compile_option_pricing_cpp():
    with subprocess.Popen(
        ["g++", "-std=c++20", "-O3", "option_pricing.cpp"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
    ) as process:
        pass


if __name__ == "__main__":
    compile_option_pricing_cpp()
    start_time = time.time()
    cards = Cards(20)

    cards.set_chosen_cards([])

    call_price, put_price, call_delta, put_delta = option_pricing_cpp(cards)
    end_time = time.time()
    call_price_py, put_price_py = option_pricing(150, 130, cards)
    print("Time taken:", end_time - start_time, "seconds")

    print("Theo: ", cards.get_theoretical_price())

    print("cpp 150 Call: ", call_price)
    print("py  150 Call: ", call_price_py)
    print("cpp 130 Put:", put_price)
    print("py  130 Put:", put_price_py)

    print(
        "Call Delta:",
        call_delta,
    )
    print(
        "Put Delta:",
        put_delta,
    )
