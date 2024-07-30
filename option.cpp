#include <algorithm>
#include <cassert>
#include <chrono>
#include <future>
#include <iostream>
#include <numeric>
#include <random>
#include <vector>

class Cards {
 public:
  Cards() { reset_card_counts(); }
  void choose_card(double card) {
    assert(card_counts[card] > 0);
    chosen_cards.push_back(card);
    card_counts[card]--;
  }

  void set_chosen_cards(const std::vector<double>& cards) {
    chosen_cards = cards;
    reset_card_counts();
    for (const auto& card : cards) {
      card_counts[static_cast<int>(card)]--;
    }
  }

  [[nodiscard]] double get_chosen_cards_sum() const {
    return std::accumulate(std::begin(chosen_cards), std::end(chosen_cards),
                           0.0);
  }

  [[nodiscard]] std::vector<double> get_remaining_cards() const {
    std::vector<double> remaining_cards;
    for (int i = 1; i <= 13; i++) {
      for (int j = 0; j < card_counts[i]; j++) {
        remaining_cards.push_back(i);
      }
    }
    return remaining_cards;
  }

  [[nodiscard]] int get_remaining_cards_to_choose() const {
    return total_cards_to_choose - chosen_cards.size();
  }

  [[nodiscard]] double get_expected_value() const {
    const auto cards = get_remaining_cards();
    return std::accumulate(std::begin(cards), std::end(cards), 0.0) /
           cards.size();
  }

  [[nodiscard]] double get_theoretical_price() const {
    return get_expected_value() * get_remaining_cards_to_choose() +
           get_chosen_cards_sum();
  }

 private:
  void reset_card_counts() { card_counts.fill(4); }

  const std::vector<double> all_cards{
      1.0,  1.0,  1.0,  1.0,  2.0,  2.0,  2.0,  2.0,  3.0,  3.0,  3.0,
      3.0,  4.0,  4.0,  4.0,  4.0,  5.0,  5.0,  5.0,  5.0,  6.0,  6.0,
      6.0,  6.0,  7.0,  7.0,  7.0,  7.0,  8.0,  8.0,  8.0,  8.0,  9.0,
      9.0,  9.0,  9.0,  10.0, 10.0, 10.0, 10.0, 11.0, 11.0, 11.0, 11.0,
      12.0, 12.0, 12.0, 12.0, 13.0, 13.0, 13.0, 13.0};
  std::vector<double> chosen_cards{};
  std::array<uint8_t, 14> card_counts{};
  uint8_t total_cards_to_choose = 20;
};

inline double call_payoff(double strike_price, double underlying_price) {
  if (underlying_price > strike_price) {
    return underlying_price - strike_price;
  }
  return 0;
}

inline double put_payoff(double strike_price, double underlying_price) {
  if (underlying_price < strike_price) {
    return strike_price - underlying_price;
  }
  return 0;
}
static constexpr uint64_t totalSimCnt = 300000;

std::pair<double, double> option_pricing(double call_strike, double put_strike,
                                         Cards cards,
                                         uint64_t iterations = 100000) {
  std::vector<double> remaining_cards = cards.get_remaining_cards();
  std::random_device rd;
  std::mt19937 g(rd());
  double call_price_sum = 0;
  double put_price_sum = 0;
  for (uint64_t c = 1; c <= iterations; c++) {
    std::shuffle(std::begin(remaining_cards), std::end(remaining_cards), g);
    double underlying_price =
        cards.get_chosen_cards_sum() +
        std::accumulate(
            std::begin(remaining_cards),
            std::begin(remaining_cards) + cards.get_remaining_cards_to_choose(),
            0);
    call_price_sum += call_payoff(call_strike, underlying_price);
    put_price_sum += put_payoff(put_strike, underlying_price);
  }
  return {call_price_sum / iterations, put_price_sum / iterations};
}

int main() {
  constexpr int threadCnt = 10;
  std::chrono::steady_clock::time_point begin =
      std::chrono::steady_clock::now();

  Cards cards;
  std::vector<std::future<std::pair<double, double>>> threads;
  double call_price_sum = 0;
  double put_price_sum = 0;

  for (int i = 0; i < threadCnt; i++) {
    threads.push_back(std::async(std::launch::async, option_pricing, 150, 130,
                                 cards, totalSimCnt));
  }
  for (int i = 0; i < threadCnt; i++) {
    threads[i].wait();
    auto ans = threads[i].get();
    call_price_sum += ans.first;
    put_price_sum += ans.second;
  }

  std::chrono::steady_clock::time_point end = std::chrono::steady_clock::now();
  std::cout << "Time difference (sec) = "
            << (std::chrono::duration_cast<std::chrono::microseconds>(end -
                                                                      begin)
                    .count()) /
                   1000000.0
            << std::endl;
  std::cout << "Iterations: " << static_cast<uint64_t>(totalSimCnt * threadCnt)
            << std::endl;
  std::cout << "Call: " << (call_price_sum / threadCnt) << "\n"
            << " Put: " << (put_price_sum / threadCnt) << "\n";
}