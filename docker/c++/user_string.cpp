#include <iostream>
#include <string>
#include <algorithm>
#include <cctype>

void solve(std::string &text, int &length) {
    std::cout << "String processing example" << std::endl;
    std::cout << "Input text: " << text << std::endl;
    
    // Convert to uppercase
    std::transform(text.begin(), text.end(), text.begin(), ::toupper);
    
    // Get length
    length = static_cast<int>(text.length());
    
    std::cout << "Output text: " << text << std::endl;
    std::cout << "Length: " << length << std::endl;
}
