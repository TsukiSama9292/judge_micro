#include <iostream>
#include <vector>
#include <numeric>

bool solve(std::vector<int> &numbers, int &sum) {
    std::cout << "Vector processing example" << std::endl;
    std::cout << "Input numbers: ";
    for (int num : numbers) {
        std::cout << num << " ";
    }
    std::cout << std::endl;
    
    // Double each number
    for (auto &num : numbers) {
        num *= 2;
    }
    
    // Calculate sum
    sum = std::accumulate(numbers.begin(), numbers.end(), 0);
    
    std::cout << "Doubled numbers: ";
    for (int num : numbers) {
        std::cout << num << " ";
    }
    std::cout << std::endl;
    std::cout << "Sum: " << sum << std::endl;
    
    return true;
}
