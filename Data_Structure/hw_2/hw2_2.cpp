#include <iostream>
#include <cstring> 
using namespace std;

const int N = 1e6;

struct Stack {
    int arr[N]; // 栈的数组
    int top;    // 栈顶指针
    Stack() : top(-1) {} // 构造函数，初始化栈顶为 -1
    void push(int value) { // 入栈
        arr[++top] = value;
    }
    void pop() { // 出栈
        if (top >= 0)
            --top;
    }
    int peek() { // 获取栈顶元素
        return arr[top];
    }
    bool isEmpty() { // 判断栈是否为空
        return top == -1;
    }
};

struct Result {
    int maxLength;   // 最长有效括号的长度
    int startIndex;  // 最长有效括号的起始索引
};

int main() {
    char s[N];
    cin >> s; // 读取字符数组

    int n = strlen(s); // 获取字符数组的长度
    if (n == 1 || n == 0) {
        cout << 0 << " " << 0;
        return 0;
    }

    Stack stk; // 创建栈
    stk.push(-1); // 初始化栈，先放一个 -1

    Result res = {0, 0}; // 初始化结果结构体

    for (int i = 0; s[i] != '\0'; ++i) { // 使用 '\0' 判断结束
        if (s[i] == '(') {
            stk.push(i); // 入栈当前索引
        } else {
            stk.pop(); // 出栈
            if (stk.isEmpty()) {
                stk.push(i); // 如果栈为空，压入当前索引
            } else {
                if (i - stk.peek() > res.maxLength) {
                    res.maxLength = i - stk.peek(); // 更新最大长度
                    res.startIndex = stk.peek() + 1; // 更新起始索引
                }
            }
        }
    }
    cout << res.maxLength << " " << res.startIndex << endl;

    return 0;
}


