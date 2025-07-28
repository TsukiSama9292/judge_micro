#include <stdio.h>

int solve(int *a, int *b) {
    // C11 特性：匿名結構體
    struct {
        union {
            int x;
            int y;
        };
        int z;
    } test_struct = {.x = 42, .z = 100};
    
    printf("C11 anonymous struct test: x=%d, z=%d\n", test_struct.x, test_struct.z);
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
