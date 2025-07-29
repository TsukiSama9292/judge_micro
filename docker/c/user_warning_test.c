#include <stdio.h>

int solve(int *result) {
    int unused_variable = 42;  // Unused variable warning
    char buffer[5];
    strcpy(buffer, "This is too long");  // Buffer overflow risk
    
    *result = 100;
    return 0;  // Missing return value
}
