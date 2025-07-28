// 階乘範例：計算輸入數字的階乘
int solve(int *n, int *factorial) {
    printf("計算 %d 的階乘\n", *n);
    
    if (*n < 0) {
        printf("錯誤：階乘不能計算負數\n");
        *factorial = -1;
        return -1;
    }
    
    *factorial = 1;
    for (int i = 1; i <= *n; i++) {
        *factorial *= i;
    }
    
    printf("結果: %d! = %d\n", *n, *factorial);
    return 0;
}
