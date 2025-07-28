#include <stdio.h>

int solve(int *result) {
    int unused_variable = 42;  // 未使用變量警告
    char buffer[5];
    strcpy(buffer, "This is too long");  // 緩衝區溢出風險
    
    *result = 100;
    return 0;  // 缺少返回值
}
