#include <stdio.h>

int solve(int *a, int *b) {
    // Transform a=3 to a=6, b=4 to b=9
    *a = *a * 2;      // 3 * 2 = 6
    *b = *b * 2 + 1;  // 4 * 2 + 1 = 9
    
    return 0;
}
