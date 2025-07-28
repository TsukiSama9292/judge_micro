import pytest

def test_c():
    from judge_micro.services.efficient import judge_micro
    efficient_c_code = '''#include <stdio.h>

int solve(int *a, int *b) {
    *a = *a * 2;      // 3 * 2 = 6
    *b = *b * 2 + 1;  // 4 * 2 + 1 = 9
    printf("Hello from C user code!\\n");
    return 0;
}'''

    solve_params_test = [
        {"name": "a", "type": "int", "input_value": 3},
        {"name": "b", "type": "int", "input_value": 4}
    ]

    expected_test = {"a": 6, "b": 9}

    config = {
        "solve_params": solve_params_test,
        "expected": expected_test,
        "function_type": "int"
    }

    result_c_efficient = judge_micro.run_microservice(
        language='c',
        user_code=efficient_c_code,
        config=config,
        show_logs=True
    )
    print("C 測試結果:\n", result_c_efficient)
    assert result_c_efficient.get('status').lower() == 'success'
    assert result_c_efficient.get('match') == True

if __name__ == "__main__":
    pytest.main()