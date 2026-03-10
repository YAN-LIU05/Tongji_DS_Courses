#include <iostream>
#include <map>
#include <stack>
#include <algorithm>
using namespace std;

class FreqStack {
private:
    map<int, int> frequency_map;  // 存储元素的频率
    map<int, stack<int>> freq_map;  // 存储频率到元素的映射
    int max_freq;  // 当前栈中最大的频率

public:
    FreqStack() : max_freq(0) {}

    // 将元素 val 压入栈中
    void push(int val) {
        // 更新频率
        int freq = ++frequency_map[val];

        // 更新最大频率
        max_freq = max(max_freq, freq);

        // 将元素添加到频率栈中
        freq_map[freq].push(val);
    }

    // 从栈中弹出元素
    int pop() {
        // 获取当前最大频率栈中的顶部元素
        int val = freq_map[max_freq].top();
        freq_map[max_freq].pop();

        // 更新频率
        frequency_map[val]--;

        // 如果该频率的栈为空，更新最大频率
        if (freq_map[max_freq].empty()) {
            max_freq--;
        }

        return val;
    }
};
