#include <iostream>

int solve(int &number, int &result) {
    // Calculate square of the input number
    std::cout << "Calculating square of " << number << std::endl;
    result = number * number;
    std::cout << "Result: " << number << "^2 = " << result << std::endl;
    return 0;
}
