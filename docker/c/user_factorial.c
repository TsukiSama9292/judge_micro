// Factorial example: Calculate factorial of input number
int solve(int *n, int *factorial) {
    printf("Calculating factorial of %d\n", *n);
    
    if (*n < 0) {
        printf("Error: Factorial cannot be calculated for negative numbers\n");
        *factorial = -1;
        return -1;
    }
    
    *factorial = 1;
    for (int i = 1; i <= *n; i++) {
        *factorial *= i;
    }
    
    printf("Result: %d! = %d\n", *n, *factorial);
    return 0;
}
