#include <iostream>
#include <cstring>
using namespace std;

struct Stack {
    char arr[1000]; 
    int top;

    Stack() : top(-1) {} // 构造函数初始化栈顶指针

    void push(char c) {
        arr[++top] = c; // 压栈
    }

    void pop() {
        if (top >= 0) {
            top--; // 弹栈
        }
    }

    char topElement() {
        return arr[top]; // 获取栈顶元素
    }

    bool isEmpty() {
        return top < 0; // 检查栈是否为空
    }
};

int main() {
    char stand[1000], s[1000];

    cin >> stand; // 读取标准字符串
    while (cin >> s) { // 读取待检测字符串
        Stack st; // 创建栈对象
        int ptr = 0; // 用于遍历待检测字符串

        for (int i = 0; stand[i] != '\0'; i++) {
            if (ptr < strlen(s) && stand[i] == s[ptr]) {
                ptr++;
            } else {
                st.push(stand[i]); // 压栈
            }

            while (!st.isEmpty() && ptr < strlen(s) && st.topElement() == s[ptr]) {
                st.pop(); // 弹栈
                ptr++;
            }
        }

        // 处理完标准字符串后，检查栈中剩余字符
        while (!st.isEmpty() && ptr < strlen(s) && st.topElement() == s[ptr]) {
            st.pop(); // 弹栈
            ptr++;
        }

        cout << (ptr == strlen(s) ? "yes" : "no") << endl;
    }

    return 0;
}
