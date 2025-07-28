#include <iostream>
#include <vector>
#include <ranges>
#include <algorithm>
#include <numeric>

int solve(std::vector<int> &numbers, int &sum) {
    std::cout << "Processing vector with C++20 ranges" << std::endl;
    
    // Use C++20 ranges to transform
    std::ranges::transform(numbers, numbers.begin(), [](int x) { return x * 2; });
    
    // Use standard accumulate instead of fold_left (which is C++23)
    sum = std::accumulate(numbers.begin(), numbers.end(), 0);
    
    std::cout << "Doubled numbers and calculated sum: " << sum << std::endl;
    
    return static_cast<int>(numbers.size());
}
