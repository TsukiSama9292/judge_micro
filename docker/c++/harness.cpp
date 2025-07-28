/*
 * Config-Driven OJ Runner - C++ Version with Modern Features
 * ---------------------------------------------------------
 * - harness.cpp is universal and never changes
 * - config.json defines input values, types and function signature
 * - User function receives inputs as reference parameters
 * - Type-safe with C++17 features
 * - Enhanced error handling with exceptions
 *
 * Example config.json:
 * {
 *   "solve_params": [
 *     {"name": "a", "type": "int", "input_value": 3},
 *     {"name": "b", "type": "int", "input_value": 4}
 *   ],
 *   "expected": {"a": 6, "b": 9},
 *   "function_type": "int"
 * }
 *
 * User writes only:
 *   int solve(int &a, int &b) {
 *     a = a * 2;
 *     b = b + 5;
 *     return 0;
 *   }
 */

#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <memory>
#include <chrono>
#include <sstream>
#include <filesystem>
#include <cmath>
#include <sys/resource.h>
#include <sys/wait.h>
#include <unistd.h>
#include "json.hpp"

using json = nlohmann::json;
using namespace std::chrono;

class Timer {
public:
    void start() { start_time = high_resolution_clock::now(); }
    double elapsed_ms() const {
        auto end_time = high_resolution_clock::now();
        auto duration = duration_cast<microseconds>(end_time - start_time);
        return duration.count() / 1000.0;
    }
private:
    high_resolution_clock::time_point start_time;
};

class ResourceMonitor {
public:
    void start() { getrusage(RUSAGE_SELF, &start_usage); }
    
    struct Stats {
        double cpu_utime;
        double cpu_stime;
        double maxrss_mb;
    };
    
    Stats get_stats() const {
        rusage end_usage;
        getrusage(RUSAGE_SELF, &end_usage);
        
        double ut = (end_usage.ru_utime.tv_sec - start_usage.ru_utime.tv_sec) + 
                   (end_usage.ru_utime.tv_usec - start_usage.ru_utime.tv_usec) / 1e6;
        double st = (end_usage.ru_stime.tv_sec - start_usage.ru_stime.tv_sec) + 
                   (end_usage.ru_stime.tv_usec - start_usage.ru_stime.tv_usec) / 1e6;
        
        return {ut, st, end_usage.ru_maxrss / 1024.0};
    }
    
private:
    rusage start_usage;
};

class CodeGenerator {
public:
    static void generate_header(const json& config) {
        std::ofstream header("solve.hpp");
        if (!header) {
            throw std::runtime_error("Cannot create solve.hpp");
        }
        
        header << "// Auto-generated function header for C++ OJ Runner\n";
        header << "#ifndef SOLVE_HPP\n#define SOLVE_HPP\n\n";
        header << "#include <iostream>\n";
        header << "#include <string>\n";
        header << "#include <vector>\n";
        header << "#include <algorithm>\n";
        header << "#include <cmath>\n";
        header << "#include <cassert>\n\n";
        
        // Generate solve function signature
        header << "// User solve function\n";
        
        std::string return_type = "int";
        if (config.contains("function_type")) {
            return_type = config["function_type"].get<std::string>();
        }
        
        header << return_type << " solve(";
        
        const auto& params = config["solve_params"];
        if (params.is_array()) {
            for (size_t i = 0; i < params.size(); ++i) {
                if (i > 0) header << ", ";
                
                const std::string& name = params[i]["name"].get<std::string>();
                const std::string& type = params[i]["type"].get<std::string>();
                
                header << get_cpp_type(type) << " &" << name;
            }
        }
        header << ");\n\n";
        header << "#endif\n";
    }
    
    static void generate_test_main(const json& config) {
        std::ofstream main_file("test_main.cpp");
        if (!main_file) {
            throw std::runtime_error("Cannot create test_main.cpp");
        }
        
        main_file << "// Auto-generated test main for C++ OJ Runner\n";
        main_file << "#include <iostream>\n";
        main_file << "#include <string>\n";
        main_file << "#include <vector>\n";
        main_file << "#include <algorithm>\n";
        main_file << "#include <cmath>\n";
        main_file << "#include <cassert>\n\n";
        
        // Generate solve function declaration based on config
        const auto& params = config["solve_params"];
        std::string return_type = "int";
        if (config.contains("function_type")) {
            return_type = config["function_type"].get<std::string>();
        }
        
        main_file << "// User solve function declaration\n";
        main_file << get_cpp_type(return_type) << " solve(";
        if (params.is_array()) {
            for (size_t i = 0; i < params.size(); ++i) {
                if (i > 0) main_file << ", ";
                const auto& param = params[i];
                const std::string& type = param["type"].get<std::string>();
                const std::string& name = param["name"].get<std::string>();
                main_file << get_cpp_type(type) << " &" << name;
            }
        }
        main_file << ");\n\n";
        
        main_file << "int main() {\n";
        main_file << "    try {\n";
        
        // Initialize parameters with input values
        if (params.is_array()) {
            for (size_t i = 0; i < params.size(); ++i) {
                const auto& param = params[i];
                const std::string& name = param["name"].get<std::string>();
                const std::string& type = param["type"].get<std::string>();
                const auto& input_value = param["input_value"];
                
                main_file << "        " << get_cpp_type(type) << " " << name 
                         << " = " << format_value(type, input_value) << ";\n";
            }
        }
        
        main_file << "\n        // Call solve function\n";
        
        if (return_type == "void") {
            main_file << "        solve(";
            if (params.is_array()) {
                for (size_t i = 0; i < params.size(); ++i) {
                    if (i > 0) main_file << ", ";
                    main_file << params[i]["name"].get<std::string>();
                }
            }
            main_file << ");\n\n";
        } else {
            main_file << "        auto function_result = solve(";
            if (params.is_array()) {
                for (size_t i = 0; i < params.size(); ++i) {
                    if (i > 0) main_file << ", ";
                    main_file << params[i]["name"].get<std::string>();
                }
            }
            main_file << ");\n\n";
        }
        
        // Output final values for verification
        main_file << "        // Output final values for verification\n";
        main_file << "        std::cout << \"RESULT_START\" << std::endl;\n";
        if (params.is_array()) {
            for (size_t i = 0; i < params.size(); ++i) {
                const auto& param = params[i];
                const std::string& name = param["name"].get<std::string>();
                const std::string& type = param["type"].get<std::string>();
        main_file << "        std::cout << \"" << name << ":\" << " 
                 << format_output(type, name) << " << std::endl;\n";
            }
        }
        if (return_type == "void") {
            main_file << "        std::cout << \"return_value:void\" << std::endl;\n";
        } else {
            main_file << "        std::cout << \"return_value:\" << function_result << std::endl;\n";
        }
        main_file << "        std::cout << \"RESULT_END\" << std::endl;\n";
        
        main_file << "    } catch (const std::exception& e) {\n";
        main_file << "        std::cerr << \"Runtime error: \" << e.what() << std::endl;\n";
        main_file << "        return 1;\n";
        main_file << "    }\n";
        main_file << "    return 0;\n";
        main_file << "}\n";
    }
    
    static std::string get_cpp_type(const std::string& type) {
        if (type == "string") return "std::string";
        if (type.find("vector<") == 0) {
            std::string inner = type.substr(7, type.length() - 8);
            return "std::vector<" + get_cpp_type(inner) + ">";
        }
        return type; // int, double, float, bool, char, long, etc.
    }

private:
    
    static std::string format_value(const std::string& type, const json& value) {
        if (type == "string") {
            return "\"" + value.get<std::string>() + "\"";
        }
        if (type.find("vector<") == 0) {
            std::string result = "{";
            if (value.is_array()) {
                for (size_t i = 0; i < value.size(); ++i) {
                    if (i > 0) result += ", ";
                    result += value[i].dump();
                }
            }
            result += "}";
            return result;
        }
        if (type == "char") {
            return "'" + value.get<std::string>() + "'";
        }
        return value.dump();
    }
    
    static std::string format_output(const std::string& type, const std::string& name) {
        if (type == "string") {
            return "\"\\\"\" << " + name + " << \"\\\"\"";
        }
        if (type.find("vector<") == 0) {
            return "\"[\" << [&]() { std::string s; for(size_t i = 0; i < " + name + 
                   ".size(); ++i) { if(i > 0) s += \", \"; s += std::to_string(" + name + 
                   "[i]); } return s; }() << \"]\"";
        }
        return name;
    }
};

class ResultAnalyzer {
public:
    static json parse_output(const std::string& output, const json& /* expected */) {
        json actual;
        
        size_t start = output.find("RESULT_START");
        size_t end = output.find("RESULT_END");
        
        if (start == std::string::npos || end == std::string::npos) {
            return actual;
        }
        
        std::string result_section = output.substr(start + 12, end - start - 12);
        std::istringstream iss(result_section);
        std::string line;
        
        while (std::getline(iss, line)) {
            size_t colon = line.find(':');
            if (colon != std::string::npos) {
                std::string key = line.substr(0, colon);
                std::string value = line.substr(colon + 1);
                
                // Remove leading/trailing whitespace
                key.erase(0, key.find_first_not_of(" \t"));
                key.erase(key.find_last_not_of(" \t") + 1);
                value.erase(0, value.find_first_not_of(" \t"));
                value.erase(value.find_last_not_of(" \t") + 1);
                
                if (!key.empty() && !value.empty()) {
                    try {
                        // Check for array format [1, 2, 3, ...]
                        if (value.front() == '[' && value.back() == ']') {
                            std::vector<json> arr;
                            std::string content = value.substr(1, value.length() - 2);
                            std::istringstream ss(content);
                            std::string item;
                            while (std::getline(ss, item, ',')) {
                                item.erase(0, item.find_first_not_of(" \t"));
                                item.erase(item.find_last_not_of(" \t") + 1);
                                if (!item.empty()) {
                                    arr.push_back(json(std::stoi(item)));
                                }
                            }
                            actual[key] = json(arr);
                        }
                        // Try to parse as number first
                        else if (value.find('.') != std::string::npos) {
                            actual[key] = std::stod(value);
                        } else if (value == "true" || value == "false") {
                            actual[key] = (value == "true");
                        } else if (value.front() == '"' && value.back() == '"') {
                            actual[key] = value.substr(1, value.length() - 2);
                        } else {
                            actual[key] = static_cast<int64_t>(std::stoll(value));
                        }
                    } catch (...) {
                        actual[key] = value;
                    }
                }
            }
        }
        
        return actual;
    }
    
    static bool compare_results(const json& expected, const json& actual) {
        for (const auto& item : expected.items()) {
            const std::string& key = item.first;
            const json& expected_value = item.second;
            
            if (!actual.contains(key)) {
                return false;
            }
            
            const auto& actual_value = actual[key];
            
            // Handle floating point comparison with tolerance
            if (expected_value.is_number_float() && actual_value.is_number()) {
                double exp = expected_value.get<double>();
                double act = actual_value.get<double>();
                if (std::abs(exp - act) > 1e-9) {
                    return false;
                }
            } else if (expected_value != actual_value) {
                return false;
            }
        }
        return true;
    }
};

class OJRunner {
public:
    static int run(const std::string& config_file, const std::string& result_file) {
        try {
            // Load configuration
            json config = load_config(config_file);
            
            // Generate files
            Timer compile_timer;
            compile_timer.start();
            
            CodeGenerator::generate_test_main(config);
            
            // Compile
            auto compile_result = compile_program(config_file);
            double compile_time = compile_timer.elapsed_ms();
            
            if (!compile_result.success) {
                save_error_result(result_file, "COMPILE_ERROR", 
                                "Compilation failed", compile_result.error, 
                                compile_result.exit_code, compile_time);
                return 4;
            }
            
            // Execute
            ResourceMonitor monitor;
            Timer exec_timer;
            monitor.start();
            exec_timer.start();
            
            auto exec_result = execute_program();
            double exec_time = exec_timer.elapsed_ms();
            auto stats = monitor.get_stats();
            
            if (!exec_result.success) {
                save_error_result(result_file, "RUNTIME_ERROR", 
                                "Execution failed", exec_result.error, 
                                exec_result.exit_code, compile_time, exec_time, stats);
                return 5;
            }
            
            // Analyze results
            json result;
            result["status"] = "SUCCESS";
            result["stdout"] = exec_result.output;
            result["stderr"] = exec_result.error;
            result["time_ms"] = exec_time;
            result["cpu_utime"] = stats.cpu_utime;
            result["cpu_stime"] = stats.cpu_stime;
            result["maxrss_mb"] = stats.maxrss_mb;
            result["compile_time_ms"] = compile_time;
            
            // Compare with expected results
            if (config.contains("expected")) {
                const auto& expected = config["expected"];
                auto actual = ResultAnalyzer::parse_output(exec_result.output, expected);
                
                result["expected"] = expected;
                result["actual"] = actual;
                result["match"] = ResultAnalyzer::compare_results(expected, actual);
                
                if (!result["match"].get<bool>()) {
                    result["status"] = "WRONG_ANSWER";
                }
            }
            
            save_result(result_file, result);
            return 0;
            
        } catch (const std::exception& e) {
            save_error_result(result_file, "ERROR", 
                            "Internal error", e.what(), -1);
            return 1;
        }
    }

private:
    struct ProcessResult {
        bool success;
        std::string output;
        std::string error;
        int exit_code;
    };
    
    static json load_config(const std::string& filename) {
        std::ifstream file(filename);
        if (!file) {
            throw std::runtime_error("Cannot open config file: " + filename);
        }
        
        json config;
        file >> config;
        return config;
    }
    
    static ProcessResult compile_program(const std::string& config_file_path) {
        // Read config for compilation settings
        std::ifstream config_file(config_file_path);
        json config;
        config_file >> config;
        
        // Get C++ standard from config or use default
        std::string cpp_standard = "c++17";
        if (config.contains("cpp_standard")) {
            cpp_standard = config["cpp_standard"].get<std::string>();
        }
        
        // Get compiler flags from config or use defaults
        std::string compiler_flags = "-Wall -Wextra -O2";
        if (config.contains("compiler_flags")) {
            compiler_flags = config["compiler_flags"].get<std::string>();
        }
        
        std::string cmd = "g++ -std=" + cpp_standard + " " + compiler_flags + " -o test_runner test_main.cpp user.cpp 2>&1";
        
        return run_command(cmd);
    }
    
    static ProcessResult execute_program() {
        return run_command_separate("./test_runner");
    }
    
    static ProcessResult run_command(const std::string& cmd) {
        FILE* pipe = popen(cmd.c_str(), "r");
        if (!pipe) {
            return {false, "", "Failed to run command", -1};
        }
        
        std::string output;
        char buffer[4096];
        while (fgets(buffer, sizeof(buffer), pipe)) {
            output += buffer;
        }
        
        int exit_code = pclose(pipe);
        bool success = (exit_code == 0);
        
        return {success, output, output, exit_code};
    }
    
    static ProcessResult run_command_separate(const std::string& cmd) {
        // Create temporary files for stdout and stderr
        std::string stdout_file = "/tmp/oj_stdout_" + std::to_string(getpid());
        std::string stderr_file = "/tmp/oj_stderr_" + std::to_string(getpid());
        
        std::string full_cmd = cmd + " > " + stdout_file + " 2> " + stderr_file;
        int exit_code = system(full_cmd.c_str());
        
        // Read stdout
        std::string stdout_content;
        std::ifstream stdout_stream(stdout_file);
        if (stdout_stream) {
            std::string line;
            while (std::getline(stdout_stream, line)) {
                stdout_content += line + "\n";
            }
            stdout_stream.close();
        }
        
        // Read stderr
        std::string stderr_content;
        std::ifstream stderr_stream(stderr_file);
        if (stderr_stream) {
            std::string line;
            while (std::getline(stderr_stream, line)) {
                stderr_content += line + "\n";
            }
            stderr_stream.close();
        }
        
        // Clean up temporary files
        std::remove(stdout_file.c_str());
        std::remove(stderr_file.c_str());
        
        bool success = (exit_code == 0);
        return {success, stdout_content, stderr_content, exit_code};
    }
    
    static void save_result(const std::string& filename, const json& result) {
        std::ofstream file(filename);
        if (file) {
            // Manually control JSON field order to match C version
            file << "{\n";
            
            // Required fields in specific order
            if (result.contains("status")) {
                file << "  \"status\": " << result["status"] << ",\n";
            }
            if (result.contains("stdout")) {
                file << "  \"stdout\": " << result["stdout"] << ",\n";
            }
            if (result.contains("stderr")) {
                file << "  \"stderr\": " << result["stderr"] << ",\n";
            }
            if (result.contains("time_ms")) {
                file << "  \"time_ms\": " << result["time_ms"] << ",\n";
            }
            if (result.contains("cpu_utime")) {
                file << "  \"cpu_utime\": " << result["cpu_utime"] << ",\n";
            }
            if (result.contains("cpu_stime")) {
                file << "  \"cpu_stime\": " << result["cpu_stime"] << ",\n";
            }
            if (result.contains("maxrss_mb")) {
                file << "  \"maxrss_mb\": " << result["maxrss_mb"] << ",\n";
            }
            if (result.contains("compile_time_ms")) {
                file << "  \"compile_time_ms\": " << result["compile_time_ms"];
                if (result.contains("expected") || result.contains("actual") || result.contains("match")) {
                    file << ",\n";
                } else {
                    file << "\n";
                }
            }
            if (result.contains("expected")) {
                file << "  \"expected\": " << result["expected"];
                if (result.contains("actual") || result.contains("match")) {
                    file << ",\n";
                } else {
                    file << "\n";
                }
            }
            if (result.contains("actual")) {
                file << "  \"actual\": " << result["actual"];
                if (result.contains("match")) {
                    file << ",\n";
                } else {
                    file << "\n";
                }
            }
            if (result.contains("match")) {
                file << "  \"match\": " << (result["match"].get<bool>() ? "true" : "false") << "\n";
            }
            
            file << "}\n";
        }
    }
    
    static void save_error_result(const std::string& filename, 
                                const std::string& status,
                                const std::string& error,
                                const std::string& details,
                                int exit_code,
                                double compile_time = 0,
                                double exec_time = 0,
                                const ResourceMonitor::Stats& stats = {0, 0, 0}) {
        json result;
        result["status"] = status;
        result["error"] = error;
        result["stderr"] = details;
        result["exit_code"] = static_cast<int64_t>(exit_code);
        result["compile_time_ms"] = compile_time;
        if (exec_time > 0) {
            result["time_ms"] = exec_time;
            result["cpu_utime"] = stats.cpu_utime;
            result["cpu_stime"] = stats.cpu_stime;
            result["maxrss_mb"] = stats.maxrss_mb;
        }
        save_result(filename, result);
    }
};

int main(int argc, char* argv[]) {
    if (argc != 3) {
        std::cerr << "Usage: " << argv[0] << " config.json result.json" << std::endl;
        return 1;
    }
    
    return OJRunner::run(argv[1], argv[2]);
}
