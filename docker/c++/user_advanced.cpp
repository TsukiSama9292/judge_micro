#include <iostream>
#include <algorithm>

int solve(int &num1, int &num2, int &gcd_result, int &lcm_result) {
    std::cout << "Calculating GCD and LCM of " << num1 << " and " << num2 << std::endl;
    
    if (num1 <= 0 || num2 <= 0) {
        std::cout << "Error: Inputs must be positive integers" << std::endl;
        return -1;
    }
    
    // Calculate GCD using Euclidean algorithm
    int a = num1, b = num2;
    while (b != 0) {
        int temp = b;
        b = a % b;
        a = temp;
    }
    gcd_result = a;
    
    // Calculate LCM using the formula: LCM(a,b) = (a*b)/GCD(a,b)
    lcm_result = (num1 * num2) / gcd_result;
    
    std::cout << "GCD(" << num1 << ", " << num2 << ") = " << gcd_result << std::endl;
    std::cout << "LCM(" << num1 << ", " << num2 << ") = " << lcm_result << std::endl;
    
    return 0;
}
