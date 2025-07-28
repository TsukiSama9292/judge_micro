// 平方範例：計算輸入數字的平方
int solve(int *number, int *result) {
    printf("計算 %d 的平方\n", *number);
    *result = (*number) * (*number);
    printf("結果: %d^2 = %d\n", *number, *result);
    return 0;
}
