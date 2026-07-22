/**
 * @name    template.cpp
 * @brief   p142模板程序
 * @date    2022-12-02
*/

#include <iostream>
#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <ctime>
#include <cmath>
#include <string>
#include <vector>
#include <queue>
#include <stack>
#include <map>
#include <set>
using namespace std;

/********************************/
/*     以下是你需要提交的代码     */
/********************************/
class FreqStack {
public:
    FreqStack() {
        // 这里填写你的代码
    }
    
    void push(int val) {
        // 这里填写你的代码
    }
    
    int pop() {
        // 这里填写你的代码
    }
};
/********************************/
/*     以上是你需要提交的代码     */
/********************************/

int main() {
    int n;
    std::cin >> n;
    FreqStack fs;
    while (n --) {
        std::string order;
        std::cin >> order;
        if (order == "push") {
            int val;
            std::cin >> val;
            fs.push(val);
        }
        else if (order == "pop") {
            std::cout << fs.pop() << std::endl;
        }
    }
    return 0;
}
