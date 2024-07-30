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

  [[nodiscard]] double get_largest_remaining_card() const {
    for (int i = 13; i >= 1; i--) {
      if (card_counts[i] > 0) {
        return i;
      }
    }
    throw std::runtime_error("No cards left");
  }

  [[nodiscard]] double get_smallest_remaining_card() const {
    for (int i = 1; i <= 13; i++) {
      if (card_counts[i] > 0) {
        return i;
      }
    }
    throw std::runtime_error("No cards left");
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

std::pair<double, double> option_pricing(double call_strike, double put_strike,
                                         Cards cards, uint64_t iterations) {
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

int main(int argc, char* argv[]) {
  if (argc != 3) {
    throw std::runtime_error("Usage: option <thread_count> <iteration_count>");
  }
  std::ios::sync_with_stdio(false);

  // read thread count from command line
  const uint64_t thread_count = std::stoull(argv[1]);
  const uint64_t total_simulation_iterations = std::stoull(argv[2]);

  Cards cards;

  // read in the input
  int cnt = 0;
  std::cin >> cnt;
  while (cnt--) {
    double res;
    std::cin >> res;
    cards.choose_card(res);
  }
  std::chrono::steady_clock::time_point begin =
      std::chrono::steady_clock::now();

  Cards cards_delta = cards;
  if (cards.get_theoretical_price() <= 140) {
    cards_delta.choose_card(cards.get_largest_remaining_card());
  } else {
    cards_delta.choose_card(cards.get_smallest_remaining_card());
  }
  std::vector<std::future<std::pair<double, double>>> option_threads;
  std::vector<std::future<std::pair<double, double>>> delta_threads;
  double call_price_sum = 0;
  double put_price_sum = 0;
  double delta_call_price_sum = 0;
  double delta_put_price_sum = 0;

  for (int i = 0; i < thread_count; i++) {
    option_threads.push_back(std::async(std::launch::async, option_pricing, 150,
                                        130, cards,
                                        total_simulation_iterations));
  }
  for (int i = 0; i < thread_count; i++) {
    delta_threads.push_back(std::async(std::launch::async, option_pricing, 150,
                                       130, cards_delta,
                                       total_simulation_iterations));
  }
  for (int i = 0; i < thread_count; i++) {
    option_threads[i].wait();
    auto ans = option_threads[i].get();
    call_price_sum += ans.first;
    put_price_sum += ans.second;
  }
  for (int i = 0; i < thread_count; i++) {
    delta_threads[i].wait();
    auto ans = delta_threads[i].get();
    delta_call_price_sum += ans.first;
    delta_put_price_sum += ans.second;
  }
  double call_price = call_price_sum / thread_count;
  double put_price = put_price_sum / thread_count;
  double delta_call_price = delta_call_price_sum / thread_count;
  double delta_put_price = delta_put_price_sum / thread_count;

  double delta_underlying_price =
      cards_delta.get_theoretical_price() - cards.get_theoretical_price();
  double delta_call = (delta_call_price - call_price) / delta_underlying_price;
  double delta_put = (delta_put_price - put_price) / delta_underlying_price;
  std::chrono::steady_clock::time_point end = std::chrono::steady_clock::now();
  std::cerr << "Time difference (sec) = "
            << (std::chrono::duration_cast<std::chrono::microseconds>(end -
                                                                      begin)
                    .count()) /
                   1000000.0
            << "\n";

  std::cerr << "Iterations = " << static_cast<uint64_t>(total_simulation_iterations * thread_count)
            << "\n";
  std::cout << (call_price) << "\n" << (put_price) << "\n";
  std::cout << (delta_call) << "\n" << (delta_put) << "\n";
}