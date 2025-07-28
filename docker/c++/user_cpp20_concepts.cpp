#include <iostream>
#include <concepts>

template<typename T>
concept Numeric = std::integral<T> || std::floating_point<T>;

template<Numeric T>
T calculate_square(T value) {
    return value * value;
}

int solve(int &number, int &result) {
    std::cout << "C++20 Concepts example" << std::endl;
    std::cout << "Input number: " << number << std::endl;
    
    result = calculate_square(number);
    
    std::cout << "Square using concepts: " << result << std::endl;
    
    return 0;
}
