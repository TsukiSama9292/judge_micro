// Square example: Calculate square of input number
int solve(int *number, int *result) {
    printf("Calculating square of %d\n", *number);
    *result = (*number) * (*number);
    printf("Result: %d^2 = %d\n", *number, *result);
    return 0;
}
