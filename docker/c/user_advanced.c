// Advanced example: Multi-parameter calculation (Greatest Common Divisor and Least Common Multiple)
int gcd(int a, int b) {
    while (b != 0) {
        int temp = b;
        b = a % b;
        a = temp;
    }
    return a;
}

int solve(int *num1, int *num2, int *gcd_result, int *lcm_result) {
    printf("Calculating GCD and LCM of %d and %d\n", *num1, *num2);
    
    if (*num1 <= 0 || *num2 <= 0) {
        printf("Error: Input must be positive integers\n");
        return -1;
    }
    
    *gcd_result = gcd(*num1, *num2);
    *lcm_result = (*num1 * *num2) / *gcd_result;
    
    printf("GCD(%d, %d) = %d\n", *num1, *num2, *gcd_result);
    printf("LCM(%d, %d) = %d\n", *num1, *num2, *lcm_result);
    
    return 0;
}
