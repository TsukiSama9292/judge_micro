// 故意包含編譯錯誤的測試代碼
#include <stdio.h>

int solve(int *result) {
    // 錯誤1: 未聲明的變量
    *result = undefined_variable + 42;
    
    // 錯誤2: 語法錯誤
    if (result == NULL {
        return -1;
    }
    
    // 錯誤3: 類型不匹配
    char *str = 123;
    printf("String: %s\n", str);
    
    return 0;
}
