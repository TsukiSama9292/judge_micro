// 進階範例：多參數計算（最大公約數和最小公倍數）
int gcd(int a, int b) {
    while (b != 0) {
        int temp = b;
        b = a % b;
        a = temp;
    }
    return a;
}

int solve(int *num1, int *num2, int *gcd_result, int *lcm_result) {
    printf("計算 %d 和 %d 的最大公約數和最小公倍數\n", *num1, *num2);
    
    if (*num1 <= 0 || *num2 <= 0) {
        printf("錯誤：輸入必須是正整數\n");
        return -1;
    }
    
    *gcd_result = gcd(*num1, *num2);
    *lcm_result = (*num1 * *num2) / *gcd_result;
    
    printf("GCD(%d, %d) = %d\n", *num1, *num2, *gcd_result);
    printf("LCM(%d, %d) = %d\n", *num1, *num2, *lcm_result);
    
    return 0;
}
