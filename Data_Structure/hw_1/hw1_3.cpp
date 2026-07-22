#include <iostream>
#include <cstring>
using namespace std;
 
const int maxn = 1024;  // 数字表示的最大大小
int A[maxn], Apow[maxn], I[maxn], MUL[maxn], ANS[maxn];
 
// 打印由数组表示的大数
void print(int* c) {
    bool started = false;  // 是否开始打印
    for (int i = maxn - 1; i >= 0; i--) {
        if (c[i]) started = true;  // 找到第一个非零数字
        if (started) cout << c[i];  // 打印数字
    }
    if (!started) cout << "0";  // 如果没有打印任何数字，则输出0
    cout << endl;
}
 
// 乘法：将两个大数相乘，结果存入数组b中
void mul(int* a, int* b) {
    int c[maxn] = {0};  // 初始化结果数组为0
    for (int i = 0; i < maxn / 2; i++) {
        for (int j = 0; j < maxn / 2; j++) {
            int newn = c[i + j] + a[i] * b[j];  // 计算当前位的乘积
            c[i + j] = newn % 10;               // 保存当前位
            c[i + j + 1] += newn / 10;          // 处理进位
        }
    }
    memcpy(b, c, sizeof(c));  // 更新b为结果
}
 
// 加法：将两个大数相加，结果存入数组a中
void add(int* a, int* b) {
    for (int i = 0; i < maxn; i++) {
        a[i] += b[i];  // 相加对应位
        if (a[i] >= 10) {  // 处理进位
            a[i] -= 10;
            a[i + 1] += 1;
        }
    }
}
 
int main() {
    int n, a;
    cin >> n >> a;
 
    // 初始化A为a的数字
    A[0] = a % 10;         // 最低有效位
    A[1] = a / 10;        // 下一位
    memset(Apow, 0, sizeof(Apow));
    Apow[0] = 1;          // Apow初始化为1
 
    // 初始化ANS为零
    memset(ANS, 0, sizeof(ANS));
 
    for (int i = 1; i <= n; i++) {
        I[0] = i % 10;      // 当前i的数字
        I[1] = i / 10;      // 下一位数字
 
        mul(A, Apow);       // 计算A的i次幂
        memcpy(MUL, Apow, sizeof(MUL)); // 存储当前幂的值
 
        mul(I, MUL);        // 将当前幂与i相乘
        add(ANS, MUL);      // 将结果加到总和中
    }
 
    print(ANS);            // 输出最终结果
    return 0;
}