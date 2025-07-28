#include <iostream>
#include <cstring>

int solve(int &result) {
    [[maybe_unused]] int unused_variable = 42;  // C++17 attribute 避免警告
    char buffer[5];
    std::strcpy(buffer, "This is too long");  // 緩衝區溢出風險 (故意的)
    
    result = 100;
    return 0;
}
