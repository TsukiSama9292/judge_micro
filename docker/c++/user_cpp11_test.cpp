#include <iostream>
#include <type_traits>

int solve(int &a, int &b) {
    // C++11 特性：使用 static_assert
    static_assert(sizeof(int) >= 4, "int must be at least 4 bytes");
    
    std::cout << "C++11 feature test!" << std::endl;
    std::cout << "Input: a=" << a << ", b=" << b << std::endl;
    
    a = a * 2;
    b = b + 5;
    
    std::cout << "Output: a=" << a << ", b=" << b << std::endl;
    
    return 0;
}
