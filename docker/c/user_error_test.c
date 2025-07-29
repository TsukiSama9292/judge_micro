// Test code intentionally containing compilation errors
#include <stdio.h>

int solve(int *result) {
    // Error 1: Undeclared variable
    *result = undefined_variable + 42;
    
    // Error 2: Syntax error
    if (result == NULL {
        return -1;
    }
    
    // Error 3: Type mismatch
    char *str = 123;
    printf("String: %s\n", str);
    
    return 0;
}
