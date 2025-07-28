#include <iostream>

void solve(int &n, long long &result) {
    std::cout << "Factorial calculation example" << std::endl;
    std::cout << "Input n: " << n << std::endl;
    
    result = 1;
    for (int i = 1; i <= n; ++i) {
        result *= i;
    }
    
    std::cout << "Factorial of " << n << " is: " << result << std::endl;
}
