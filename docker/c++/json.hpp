/*
 * Simplified JSON library for C++ OJ Runner
 * Based on nlohmann/json but simplified for our specific use case
 * This is a minimal implementation that supports our requirements
 */

#ifndef JSON_HPP
#define JSON_HPP

#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <variant>
#include <type_traits>
#include <sstream>
#include <fstream>
#include <functional>

namespace nlohmann {

class json {
public:
    using value_type = std::variant<
        std::nullptr_t,
        bool,
        int64_t,
        double,
        std::string,
        std::vector<json>,
        std::map<std::string, json>
    >;

private:
    value_type data;

public:
    // Default constructor
    json() : data(nullptr) {}
    
    // Constructor from nullptr
    json(std::nullptr_t) : data(nullptr) {}
    
    // Constructor from bool
    json(bool value) : data(value) {}
    
    // Constructor from integers
    template<typename T>
    json(T value, typename std::enable_if<std::is_integral<T>::value && !std::is_same<T, bool>::value>::type* = nullptr)
        : data(static_cast<int64_t>(value)) {}
    
    // Constructor from floating point
    template<typename T>
    json(T value, typename std::enable_if<std::is_floating_point<T>::value>::type* = nullptr)
        : data(static_cast<double>(value)) {}
    
    // Constructor from string
    json(const std::string& value) : data(value) {}
    json(const char* value) : data(std::string(value)) {}
    
    // Constructor from vector
    json(const std::vector<json>& value) : data(value) {}
    
    // Constructor from map
    json(const std::map<std::string, json>& value) : data(value) {}
    
    // Constructor from initializer list for objects
    json(std::initializer_list<std::pair<std::string, json>> init) {
        std::map<std::string, json> obj;
        for (const auto& pair : init) {
            obj[pair.first] = pair.second;
        }
        data = obj;
    }
    
    // Object access operator
    json& operator[](const std::string& key) {
        if (!std::holds_alternative<std::map<std::string, json>>(data)) {
            data = std::map<std::string, json>();
        }
        return std::get<std::map<std::string, json>>(data)[key];
    }
    
    const json& operator[](const std::string& key) const {
        if (std::holds_alternative<std::map<std::string, json>>(data)) {
            const auto& obj = std::get<std::map<std::string, json>>(data);
            auto it = obj.find(key);
            if (it != obj.end()) {
                return it->second;
            }
        }
        static json null_json;
        return null_json;
    }
    
    // Array access operator
    json& operator[](size_t index) {
        if (!std::holds_alternative<std::vector<json>>(data)) {
            data = std::vector<json>();
        }
        auto& arr = std::get<std::vector<json>>(data);
        if (index >= arr.size()) {
            arr.resize(index + 1);
        }
        return arr[index];
    }
    
    const json& operator[](size_t index) const {
        if (std::holds_alternative<std::vector<json>>(data)) {
            const auto& arr = std::get<std::vector<json>>(data);
            if (index < arr.size()) {
                return arr[index];
            }
        }
        static json null_json;
        return null_json;
    }
    
    // Check if contains key
    bool contains(const std::string& key) const {
        if (std::holds_alternative<std::map<std::string, json>>(data)) {
            const auto& obj = std::get<std::map<std::string, json>>(data);
            return obj.find(key) != obj.end();
        }
        return false;
    }
    
    // Type checking
    bool is_null() const { return std::holds_alternative<std::nullptr_t>(data); }
    bool is_boolean() const { return std::holds_alternative<bool>(data); }
    bool is_number_integer() const { return std::holds_alternative<int64_t>(data); }
    bool is_number_float() const { return std::holds_alternative<double>(data); }
    bool is_number() const { return is_number_integer() || is_number_float(); }
    bool is_string() const { return std::holds_alternative<std::string>(data); }
    bool is_array() const { return std::holds_alternative<std::vector<json>>(data); }
    bool is_object() const { return std::holds_alternative<std::map<std::string, json>>(data); }
    
    // Size for arrays and objects
    size_t size() const {
        if (is_array()) {
            return std::get<std::vector<json>>(data).size();
        } else if (is_object()) {
            return std::get<std::map<std::string, json>>(data).size();
        }
        return 0;
    }
    
    // Get values with type casting
    template<typename T>
    T get() const {
        if constexpr (std::is_same_v<T, bool>) {
            if (std::holds_alternative<bool>(data)) {
                return std::get<bool>(data);
            }
        } else if constexpr (std::is_integral_v<T>) {
            if (std::holds_alternative<int64_t>(data)) {
                return static_cast<T>(std::get<int64_t>(data));
            } else if (std::holds_alternative<double>(data)) {
                return static_cast<T>(std::get<double>(data));
            }
        } else if constexpr (std::is_floating_point_v<T>) {
            if (std::holds_alternative<double>(data)) {
                return static_cast<T>(std::get<double>(data));
            } else if (std::holds_alternative<int64_t>(data)) {
                return static_cast<T>(std::get<int64_t>(data));
            }
        } else if constexpr (std::is_same_v<T, std::string>) {
            if (std::holds_alternative<std::string>(data)) {
                return std::get<std::string>(data);
            }
        }
        throw std::runtime_error("Cannot convert JSON value to requested type");
    }
    
    // Assignment operators
    json& operator=(bool value) { data = value; return *this; }
    json& operator=(int value) { data = static_cast<int64_t>(value); return *this; }
    json& operator=(int64_t value) { data = value; return *this; }
    json& operator=(long long value) { data = static_cast<int64_t>(value); return *this; }
    json& operator=(double value) { data = value; return *this; }
    json& operator=(const std::string& value) { data = value; return *this; }
    json& operator=(const char* value) { data = std::string(value); return *this; }
    
    // Comparison operators
    bool operator==(const json& other) const {
        return data == other.data;
    }
    
    bool operator!=(const json& other) const {
        return !(*this == other);
    }
    
    // Iterator support for objects
    class iterator_pair {
    public:
        std::string key;
        json& value;
        iterator_pair(const std::string& k, json& v) : key(k), value(v) {}
    };
    
    std::vector<iterator_pair> items() {
        std::vector<iterator_pair> result;
        if (is_object()) {
            auto& obj = std::get<std::map<std::string, json>>(data);
            for (auto& pair : obj) {
                result.emplace_back(pair.first, pair.second);
            }
        }
        return result;
    }
    
    std::vector<std::pair<std::string, const json&>> items() const {
        std::vector<std::pair<std::string, const json&>> result;
        if (is_object()) {
            const auto& obj = std::get<std::map<std::string, json>>(data);
            for (const auto& pair : obj) {
                result.emplace_back(pair.first, std::cref(pair.second));
            }
        }
        return result;
    }
    
    // Parse from string
    static json parse(const std::string& str) {
        // Simplified parser - this is a basic implementation
        // In a real implementation, you'd want a proper JSON parser
        std::istringstream iss(str);
        return parse_value(iss);
    }
    
    // Parse from stream
    static json parse(std::istream& stream) {
        return parse_value(stream);
    }
    
    // Dump to string
    std::string dump(int indent = -1) const {
        std::ostringstream oss;
        dump_value(oss, 0, indent);
        return oss.str();
    }

private:
    static json parse_value(std::istream& stream) {
        skip_whitespace(stream);
        char c = stream.peek();
        
        if (c == '"') {
            return json(parse_string(stream));
        } else if (c == '{') {
            return parse_object(stream);
        } else if (c == '[') {
            return parse_array(stream);
        } else if (c == 't' || c == 'f') {
            return json(parse_bool(stream));
        } else if (c == 'n') {
            parse_null(stream);
            return json();
        } else if (c == '-' || std::isdigit(c)) {
            return parse_number(stream);
        }
        
        throw std::runtime_error("Unexpected character in JSON");
    }
    
    static void skip_whitespace(std::istream& stream) {
        while (stream && std::isspace(stream.peek())) {
            stream.get();
        }
    }
    
    static std::string parse_string(std::istream& stream) {
        stream.get(); // consume opening quote
        std::string result;
        char c;
        while (stream.get(c) && c != '"') {
            if (c == '\\') {
                stream.get(c);
                switch (c) {
                    case 'n': result += '\n'; break;
                    case 't': result += '\t'; break;
                    case 'r': result += '\r'; break;
                    case 'b': result += '\b'; break;
                    case 'f': result += '\f'; break;
                    case '"': result += '"'; break;
                    case '\\': result += '\\'; break;
                    case '/': result += '/'; break;
                    default: result += c; break;
                }
            } else {
                result += c;
            }
        }
        return result;
    }
    
    static json parse_object(std::istream& stream) {
        stream.get(); // consume '{'
        std::map<std::string, json> obj;
        
        skip_whitespace(stream);
        if (stream.peek() == '}') {
            stream.get();
            return json(obj);
        }
        
        while (stream) {
            skip_whitespace(stream);
            std::string key = parse_string(stream);
            skip_whitespace(stream);
            
            if (stream.get() != ':') {
                throw std::runtime_error("Expected ':' in object");
            }
            
            skip_whitespace(stream);
            obj[key] = parse_value(stream);
            skip_whitespace(stream);
            
            char next = stream.get();
            if (next == '}') break;
            if (next != ',') {
                throw std::runtime_error("Expected ',' or '}' in object");
            }
        }
        
        return json(obj);
    }
    
    static json parse_array(std::istream& stream) {
        stream.get(); // consume '['
        std::vector<json> arr;
        
        skip_whitespace(stream);
        if (stream.peek() == ']') {
            stream.get();
            return json(arr);
        }
        
        while (stream) {
            skip_whitespace(stream);
            arr.push_back(parse_value(stream));
            skip_whitespace(stream);
            
            char next = stream.get();
            if (next == ']') break;
            if (next != ',') {
                throw std::runtime_error("Expected ',' or ']' in array");
            }
        }
        
        return json(arr);
    }
    
    static bool parse_bool(std::istream& stream) {
        std::string str;
        char c;
        while (stream.get(c) && std::isalpha(c)) {
            str += c;
        }
        stream.unget();
        
        if (str == "true") return true;
        if (str == "false") return false;
        throw std::runtime_error("Invalid boolean value");
    }
    
    static void parse_null(std::istream& stream) {
        std::string str;
        char c;
        while (stream.get(c) && std::isalpha(c)) {
            str += c;
        }
        stream.unget();
        
        if (str != "null") {
            throw std::runtime_error("Invalid null value");
        }
    }
    
    static json parse_number(std::istream& stream) {
        std::string str;
        char c;
        bool has_dot = false;
        
        while (stream.get(c) && (std::isdigit(c) || c == '.' || c == '-' || c == '+' || c == 'e' || c == 'E')) {
            str += c;
            if (c == '.') has_dot = true;
        }
        stream.unget();
        
        if (has_dot) {
            return json(std::stod(str));
        } else {
            return json(std::stoll(str));
        }
    }
    
    void dump_value(std::ostream& stream, int depth, int indent) const {
        std::visit([&](const auto& value) {
            using T = std::decay_t<decltype(value)>;
            if constexpr (std::is_same_v<T, std::nullptr_t>) {
                stream << "null";
            } else if constexpr (std::is_same_v<T, bool>) {
                stream << (value ? "true" : "false");
            } else if constexpr (std::is_same_v<T, int64_t>) {
                stream << value;
            } else if constexpr (std::is_same_v<T, double>) {
                stream << value;
            } else if constexpr (std::is_same_v<T, std::string>) {
                stream << '"';
                for (char c : value) {
                    switch (c) {
                        case '"': stream << "\\\""; break;
                        case '\\': stream << "\\\\"; break;
                        case '\n': stream << "\\n"; break;
                        case '\t': stream << "\\t"; break;
                        case '\r': stream << "\\r"; break;
                        case '\b': stream << "\\b"; break;
                        case '\f': stream << "\\f"; break;
                        default: stream << c; break;
                    }
                }
                stream << '"';
            } else if constexpr (std::is_same_v<T, std::vector<json>>) {
                stream << '[';
                for (size_t i = 0; i < value.size(); ++i) {
                    if (i > 0) stream << ',';
                    if (indent >= 0) {
                        stream << '\n';
                        for (int j = 0; j <= depth; ++j) {
                            for (int k = 0; k < indent; ++k) stream << ' ';
                        }
                    }
                    value[i].dump_value(stream, depth + 1, indent);
                }
                if (indent >= 0 && !value.empty()) {
                    stream << '\n';
                    for (int j = 0; j < depth; ++j) {
                        for (int k = 0; k < indent; ++k) stream << ' ';
                    }
                }
                stream << ']';
            } else if constexpr (std::is_same_v<T, std::map<std::string, json>>) {
                stream << '{';
                size_t i = 0;
                for (const auto& pair : value) {
                    if (i > 0) stream << ',';
                    if (indent >= 0) {
                        stream << '\n';
                        for (int j = 0; j <= depth; ++j) {
                            for (int k = 0; k < indent; ++k) stream << ' ';
                        }
                    }
                    stream << '"' << pair.first << '"' << ':';
                    if (indent >= 0) stream << ' ';
                    pair.second.dump_value(stream, depth + 1, indent);
                    ++i;
                }
                if (indent >= 0 && !value.empty()) {
                    stream << '\n';
                    for (int j = 0; j < depth; ++j) {
                        for (int k = 0; k < indent; ++k) stream << ' ';
                    }
                }
                stream << '}';
            }
        }, data);
    }
};

// Stream operators
inline std::ostream& operator<<(std::ostream& stream, const json& j) {
    stream << j.dump();
    return stream;
}

inline std::istream& operator>>(std::istream& stream, json& j) {
    j = json::parse(stream);
    return stream;
}

} // namespace nlohmann

#endif // JSON_HPP
