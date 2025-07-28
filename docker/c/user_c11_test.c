#include <stdio.h>

int solve(int *a, int *b) {
    // C11 特性：使用 _Static_assert
    _Static_assert(sizeof(int) >= 4, "int must be at least 4 bytes");
    
    printf("C11 feature test!\n");
    printf("Input: a=%d, b=%d\n", *a, *b);
    
    *a = *a * 2;
    *b = *b + 5;
    
    printf("Output: a=%d, b=%d\n", *a, *b);
    printf("RESULT_START\n");
    printf("a:%d\n", *a);
    printf("b:%d\n", *b);
    printf("return_value:0\n");
    printf("RESULT_END\n");
    
    return 0;
}
