#include <vector>
#include <algorithm>
#include <numeric>
#include <iostream>
#include <random>
#include <cassert>
#include <chrono>
#include <future>

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

static constexpr std::array origCards{
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
};

static constexpr std::array constCards{
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
};
static std::array cards = constCards;
static constexpr int numCardToPickTotal = 20;
static constexpr int numCardToPick = numCardToPickTotal - (origCards.size() - constCards.size());
static constexpr double cardsSum = std::accumulate(constCards.begin(), constCards.end(), 0.0);
static constexpr double origSum = std::accumulate(origCards.begin(), origCards.end(), 0.0);
static constexpr double pickedSum = origSum - cardsSum;
static constexpr double pickedEV = cardsSum / constCards.size();
static constexpr double threadCnt = 8;
[[maybe_unused]] static constexpr double theo = pickedSum + pickedEV * numCardToPick;
static constexpr uint64_t totalSimCnt = 300000;

std::pair<double, double> compute(double iterations) {
    std::array cards = constCards;
    std::random_device rd;
    std::mt19937 g(rd());
    double call_price_sum = 0;
    double put_price_sum = 0;
    for (double cnt = 0; cnt < iterations; cnt++) {
        std::shuffle(std::begin(cards), std::end(cards), g);
        double underlying_price = pickedSum + std::accumulate(cards.begin(), cards.begin() + numCardToPick, 0);
        call_price_sum += call_payoff(150, underlying_price);
        put_price_sum += put_payoff(130, underlying_price);
        cnt++;
    }
    // std::cout << call_price_sum << " " << put_price_sum << std::endl;
    return {call_price_sum / iterations, put_price_sum / iterations};
}

int main() {
    std::cout << theo << "\n";
    std::vector<std::future<std::pair<double, double>>> threads;
    double call_price_sum = 0;
    double put_price_sum = 0;
    std::chrono::steady_clock::time_point begin = std::chrono::steady_clock::now();

    for (int i = 0; i < threadCnt; i++) {
        threads.push_back(std::async(std::launch::async, compute, totalSimCnt));
    }
    for (int i = 0; i < threadCnt; i++) {
        threads[i].wait();
        auto ans = threads[i].get();
        call_price_sum += ans.first;
        put_price_sum += ans.second;
    }

    double cnt = totalSimCnt;
    std::chrono::steady_clock::time_point end = std::chrono::steady_clock::now();
    std::cout << "Time difference (sec) = " <<  (std::chrono::duration_cast<std::chrono::microseconds>(end - begin).count()) /1000000.0  <<std::endl;
    std::cout << "Call: " << (call_price_sum / threadCnt) << " Put: " << (put_price_sum / threadCnt) << "\n";

}