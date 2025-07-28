#include <iostream>

int solve(int &result) {
    // This should cause a compilation error - undefined variable
    std::cout << "This will cause an error" << std::endl;
    result = undefined_variable; // This will cause compilation error
    return 0;
}
