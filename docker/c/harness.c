/*
 * Config-Driven OJ Runner - Pure Function Interface (Enhanced)
 * -----------------------------------------------------------
 * - harness.c is universal and never changes
 * - config.json defines input values and function signature
 * - User function receives inputs as initial parameter values
 * - Enhanced with C++ style result reporting
 *
 * Example config.json:
 * {
 *   "solve_params": [
 *     {"name": "a", "input_value": 3},
 *     {"name": "b", "input_value": 4}
 *   ],
 *   "expected": {"a": 6, "b": 9}
 * }
 *
 * User writes only:
 *   int solve(int *a, int *b) {
 *     *a = *a * 2;
 *     *b = *b + 5;
 *     return 0;
 *   }
 */

#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <math.h>
#include <sys/resource.h>
#include <sys/time.h>
#include <sys/wait.h>
#include <cjson/cJSON.h>

typedef struct {
    double cpu_utime;
    double cpu_stime;
    double maxrss_mb;
} resource_stats_t;

static double now_ms() {
    struct timeval tv; 
    gettimeofday(&tv, NULL);
    return tv.tv_sec * 1000.0 + tv.tv_usec / 1000.0;
}

static resource_stats_t get_resource_stats(struct rusage *start, struct rusage *end) {
    resource_stats_t stats;
    stats.cpu_utime = (end->ru_utime.tv_sec - start->ru_utime.tv_sec) + 
                     (end->ru_utime.tv_usec - start->ru_utime.tv_usec) / 1e6;
    stats.cpu_stime = (end->ru_stime.tv_sec - start->ru_stime.tv_sec) + 
                     (end->ru_stime.tv_usec - start->ru_stime.tv_usec) / 1e6;
    stats.maxrss_mb = end->ru_maxrss / 1024.0;
    return stats;
}

static cJSON* parse_output_results(const char* output, cJSON* expected __attribute__((unused))) {
    cJSON* actual = cJSON_CreateObject();
    
    // Find RESULT_START and RESULT_END markers
    const char* start_marker = strstr(output, "RESULT_START");
    const char* end_marker = strstr(output, "RESULT_END");
    
    if (start_marker && end_marker && start_marker < end_marker) {
        // Parse the section between markers
        const char* content_start = start_marker + strlen("RESULT_START");
        
        // Process line by line
        char* content = strndup(content_start, end_marker - content_start);
        char* line = strtok(content, "\n");
        
        while (line != NULL) {
            // Skip empty lines
            while (*line == ' ' || *line == '\t' || *line == '\r') line++;
            if (*line == '\0') {
                line = strtok(NULL, "\n");
                continue;
            }
            
            // Parse key:value pairs
            char* colon = strchr(line, ':');
            if (colon) {
                *colon = '\0';
                char* key = line;
                char* value = colon + 1;
                
                // Trim whitespace
                while (*key == ' ' || *key == '\t') key++;
                while (*value == ' ' || *value == '\t') value++;
                
                // Try to parse as number
                char* endptr;
                long long_val = strtol(value, &endptr, 10);
                if (*endptr == '\0') {
                    cJSON_AddNumberToObject(actual, key, long_val);
                } else {
                    double double_val = strtod(value, &endptr);
                    if (*endptr == '\0') {
                        cJSON_AddNumberToObject(actual, key, double_val);
                    } else {
                        cJSON_AddStringToObject(actual, key, value);
                    }
                }
            }
            line = strtok(NULL, "\n");
        }
        free(content);
    }
    
    return actual;
}

static int compare_results(cJSON* expected, cJSON* actual) {
    cJSON* item = NULL;
    cJSON_ArrayForEach(item, expected) {
        const char* key = item->string;
        cJSON* actual_item = cJSON_GetObjectItem(actual, key);
        
        if (!actual_item) return 0; // Missing key
        
        if (cJSON_IsNumber(item) && cJSON_IsNumber(actual_item)) {
            double exp_val = cJSON_GetNumberValue(item);
            double act_val = cJSON_GetNumberValue(actual_item);
            if (fabs(exp_val - act_val) > 1e-9) return 0;
        } else if (cJSON_IsString(item) && cJSON_IsString(actual_item)) {
            if (strcmp(cJSON_GetStringValue(item), cJSON_GetStringValue(actual_item)) != 0) return 0;
        } else {
            return 0; // Type mismatch
        }
    }
    return 1; // All match
}

static void save_error_result(const char* filename, const char* status, const char* error, 
                            const char* details, int exit_code, double compile_time, 
                            double exec_time, resource_stats_t* stats) {
    cJSON* result = cJSON_CreateObject();
    cJSON_AddStringToObject(result, "status", status);
    cJSON_AddStringToObject(result, "error", error);
    cJSON_AddStringToObject(result, "stderr", details ? details : "");
    cJSON_AddNumberToObject(result, "exit_code", exit_code);
    cJSON_AddNumberToObject(result, "compile_time_ms", compile_time);
    
    if (exec_time > 0) {
        cJSON_AddNumberToObject(result, "time_ms", exec_time);
        if (stats) {
            cJSON_AddNumberToObject(result, "cpu_utime", stats->cpu_utime);
            cJSON_AddNumberToObject(result, "cpu_stime", stats->cpu_stime);
            cJSON_AddNumberToObject(result, "maxrss_mb", stats->maxrss_mb);
        }
    }
    
    char* result_str = cJSON_Print(result);
    FILE* file = fopen(filename, "w");
    if (file) {
        fprintf(file, "%s\n", result_str);
        fclose(file);
    }
    free(result_str);
    cJSON_Delete(result);
}

static void generate_header(cJSON *cfg) {
    // Generate simple header without globals
    FILE *hf = fopen("solve.h", "w");
    if (!hf) { perror("Cannot create solve.h"); exit(1); }
    
    fprintf(hf, "// Auto-generated function header\n");
    fprintf(hf, "#ifndef SOLVE_H\n#define SOLVE_H\n\n");
    fprintf(hf, "#include <stdio.h>\n\n");
    
    // Generate solve function signature
    fprintf(hf, "// User solve function\n");
    
    // Get function return type from config or use default
    cJSON *function_type = cJSON_GetObjectItem(cfg, "function_type");
    const char *return_type = function_type ? cJSON_GetStringValue(function_type) : "int";
    
    fprintf(hf, "%s solve(", return_type);
    cJSON *params = cJSON_GetObjectItem(cfg, "solve_params");
    if (cJSON_IsArray(params)) {
        int count = cJSON_GetArraySize(params);
        for (int i = 0; i < count; i++) {
            if (i > 0) fprintf(hf, ", ");
            cJSON *param = cJSON_GetArrayItem(params, i);
            const char *name = cJSON_GetObjectItem(param, "name")->valuestring;
            
            // Get parameter type from config or use default
            cJSON *param_type = cJSON_GetObjectItem(param, "type");
            const char *type = param_type ? cJSON_GetStringValue(param_type) : "int";
            
            fprintf(hf, "%s *%s", type, name);
        }
    }
    fprintf(hf, ");\n\n");
    fprintf(hf, "#endif\n");
    fclose(hf);
}

static void generate_test_main(cJSON *cfg) {
    FILE *mf = fopen("test_main.c", "w");
    if (!mf) { perror("Cannot create test_main.c"); exit(1); }
    
    fprintf(mf, "// Auto-generated test main\n");
    fprintf(mf, "#include <stdio.h>\n");
    fprintf(mf, "#include \"solve.h\"\n\n");
    
    fprintf(mf, "int main() {\n");
    
    // Initialize parameters with input values
    cJSON *params = cJSON_GetObjectItem(cfg, "solve_params");
    
    if (cJSON_IsArray(params)) {
        int param_count = cJSON_GetArraySize(params);
        
        // Print input values
        fprintf(mf, "    printf(\"Hello from C user code!\\n\");\n");
        fprintf(mf, "    printf(\"Input: \");\n");
        for (int i = 0; i < param_count; i++) {
            cJSON *param = cJSON_GetArrayItem(params, i);
            const char *name = cJSON_GetObjectItem(param, "name")->valuestring;
            int input_value = cJSON_GetObjectItem(param, "input_value")->valueint;
            
            // Get parameter type from config or use default
            cJSON *param_type = cJSON_GetObjectItem(param, "type");
            const char *type = param_type ? cJSON_GetStringValue(param_type) : "int";
            
            fprintf(mf, "    %s %s = %d;\n", type, name, input_value);
            if (i > 0) fprintf(mf, "    printf(\", \");\n");
            fprintf(mf, "    printf(\"%s=%%d\", %s);\n", name, name);
        }
        fprintf(mf, "    printf(\"\\n\");\n\n");
        
        // Call solve function with proper return type
        cJSON *function_type = cJSON_GetObjectItem(cfg, "function_type");
        const char *return_type = function_type ? cJSON_GetStringValue(function_type) : "int";
        
        if (strcmp(return_type, "void") == 0) {
            fprintf(mf, "    solve(");
        } else {
            fprintf(mf, "    %s function_result = solve(", return_type);
        }
        for (int i = 0; i < param_count; i++) {
            if (i > 0) fprintf(mf, ", ");
            cJSON *param = cJSON_GetArrayItem(params, i);
            const char *name = cJSON_GetObjectItem(param, "name")->valuestring;
            fprintf(mf, "&%s", name);
        }
        fprintf(mf, ");\n\n");
        
        // Print output values
        fprintf(mf, "    printf(\"Output: \");\n");
        for (int i = 0; i < param_count; i++) {
            cJSON *param = cJSON_GetArrayItem(params, i);
            const char *name = cJSON_GetObjectItem(param, "name")->valuestring;
            if (i > 0) fprintf(mf, "    printf(\", \");\n");
            fprintf(mf, "    printf(\"%s=%%d\", %s);\n", name, name);
        }
        fprintf(mf, "    printf(\"\\n\");\n\n");
        
        // Output structured results
        fprintf(mf, "    printf(\"RESULT_START\\n\");\n");
        for (int i = 0; i < param_count; i++) {
            cJSON *param = cJSON_GetArrayItem(params, i);
            const char *name = cJSON_GetObjectItem(param, "name")->valuestring;
            fprintf(mf, "    printf(\"%s:%%d\\n\", %s);\n", name, name);
        }
        
        // Only print return value if function is not void
        if (strcmp(return_type, "void") != 0) {
            fprintf(mf, "    printf(\"return_value:%%d\\n\", function_result);\n");
        }
        fprintf(mf, "    printf(\"RESULT_END\\n\");\n");
    }
    
    fprintf(mf, "    return 0;\n}\n");
    fclose(mf);
}

int main(int argc, char **argv) {
    if (argc != 3) {
        fprintf(stderr, "Usage: %s config.json result.json\n", argv[0]);
        return 1;
    }
    
    // Load config
    FILE *fc = fopen(argv[1], "rb");
    if (!fc) { perror("fopen config"); return 2; }
    fseek(fc, 0, SEEK_END); long len = ftell(fc); fseek(fc, 0, SEEK_SET);
    char *cfgtxt = malloc(len + 1);
    fread(cfgtxt, 1, len, fc); cfgtxt[len] = '\0'; fclose(fc);

    cJSON *cfg = cJSON_Parse(cfgtxt); free(cfgtxt);
    if (!cfg) {
        fprintf(stderr, "Invalid JSON config\n");
        return 3;
    }

    // Generate all necessary files
    double compile_start = now_ms();
    generate_header(cfg);
    generate_test_main(cfg);
    
    // Get C standard from config or use default
    const cJSON* c_standard = cJSON_GetObjectItem(cfg, "c_standard");
    const char* std_flag = c_standard ? cJSON_GetStringValue(c_standard) : "c99";
    
    // Get compiler flags from config or use defaults
    const cJSON* compiler_flags = cJSON_GetObjectItem(cfg, "compiler_flags");
    const char* extra_flags = compiler_flags ? cJSON_GetStringValue(compiler_flags) : "-Wall -Wextra";
    
    // Compile everything with stderr capture
    char compile_cmd[512];
    snprintf(compile_cmd, sizeof(compile_cmd), 
             "gcc %s -std=%s -include stdio.h -o test_runner test_main.c user.c 2>&1",
             extra_flags, std_flag);
    
    FILE *compile_output = popen(compile_cmd, "r");
    if (!compile_output) {
        fprintf(stderr, "Failed to run compilation command\n");
        cJSON_Delete(cfg);
        return 4;
    }
    
    char compile_errors[4096] = {0};
    fread(compile_errors, 1, sizeof(compile_errors)-1, compile_output);
    int compile_rc = pclose(compile_output);
    double compile_time = now_ms() - compile_start;
    
    if (compile_rc != 0) {
        save_error_result(argv[2], "COMPILE_ERROR", "Compilation failed", 
                         compile_errors, compile_rc, compile_time, 0, NULL);
        cJSON_Delete(cfg);
        return 4;
    }
    
    // Execute program with resource monitoring
    struct rusage ru_start, ru_end;
    getrusage(RUSAGE_SELF, &ru_start);
    double exec_start = now_ms();
    
    // Run with separate stdout/stderr capture
    char stdout_file[64], stderr_file[64];
    snprintf(stdout_file, sizeof(stdout_file), "/tmp/oj_out_%d", getpid());
    snprintf(stderr_file, sizeof(stderr_file), "/tmp/oj_err_%d", getpid());
    
    char run_cmd[256];
    snprintf(run_cmd, sizeof(run_cmd), "./test_runner > %s 2> %s", stdout_file, stderr_file);
    int exec_rc = system(run_cmd);
    
    double exec_time = now_ms() - exec_start;
    getrusage(RUSAGE_SELF, &ru_end);
    resource_stats_t stats = get_resource_stats(&ru_start, &ru_end);
    
    // Read stdout
    char test_output[4096] = {0};
    FILE *stdout_f = fopen(stdout_file, "r");
    if (stdout_f) {
        fread(test_output, 1, sizeof(test_output)-1, stdout_f);
        fclose(stdout_f);
    }
    
    // Read stderr
    char test_stderr[4096] = {0};
    FILE *stderr_f = fopen(stderr_file, "r");
    if (stderr_f) {
        fread(test_stderr, 1, sizeof(test_stderr)-1, stderr_f);
        fclose(stderr_f);
    }
    
    // Clean up temp files
    unlink(stdout_file);
    unlink(stderr_file);
    
    if (exec_rc != 0) {
        save_error_result(argv[2], "RUNTIME_ERROR", "Execution failed", 
                         test_stderr, exec_rc, compile_time, exec_time, &stats);
        cJSON_Delete(cfg);
        return 5;
    }
    
    // Build complete result
    cJSON *result = cJSON_CreateObject();
    cJSON_AddStringToObject(result, "status", "SUCCESS");
    cJSON_AddStringToObject(result, "stdout", test_output);
    cJSON_AddStringToObject(result, "stderr", test_stderr);
    cJSON_AddNumberToObject(result, "time_ms", exec_time);
    cJSON_AddNumberToObject(result, "cpu_utime", stats.cpu_utime);
    cJSON_AddNumberToObject(result, "cpu_stime", stats.cpu_stime);
    cJSON_AddNumberToObject(result, "maxrss_mb", stats.maxrss_mb);
    cJSON_AddNumberToObject(result, "compile_time_ms", compile_time);
    
    // Compare with expected results if available
    cJSON* expected = cJSON_GetObjectItem(cfg, "expected");
    if (expected) {
        cJSON* actual = parse_output_results(test_output, expected);
        cJSON_AddItemToObject(result, "expected", cJSON_Duplicate(expected, 1));
        cJSON_AddItemToObject(result, "actual", actual);
        
        int match = compare_results(expected, actual);
        cJSON_AddBoolToObject(result, "match", match);
        
        if (!match) {
            cJSON_SetValuestring(cJSON_GetObjectItem(result, "status"), "WRONG_ANSWER");
        }
    }
    
    // Write result
    char *result_str = cJSON_Print(result);
    FILE *result_file = fopen(argv[2], "w");
    if (result_file) {
        fprintf(result_file, "%s\n", result_str);
        fclose(result_file);
    }
    
    free(result_str);
    cJSON_Delete(result);
    cJSON_Delete(cfg);
    
    return 0;
}
