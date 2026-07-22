#include <iostream>
#include <cstring>
using namespace std;
 
const int maxTerms = 2048;          // 多项式的最大项数
const int maxTermsPow2 = (int)5e6;  // 结果数组的最大大小
int polyA[maxTerms], polyB[maxTerms], sumResult[maxTermsPow2], productResult[maxTermsPow2]; // 存储多项式的数组
 
// 加法
void AddPolynomials() {
    memset(sumResult, 0, sizeof(sumResult)); // 确保加法结果数组初始化为0
    for (int i = 0; i < maxTerms; i++) 
        sumResult[i] = polyA[i] + polyB[i];
}
 
// 乘法
void MultiplyPolynomials() {
    memset(productResult, 0, sizeof(productResult)); // 确保乘法结果数组初始化为0
    for (int i = 0; i < maxTerms; i++) 
        for (int j = 0; j < maxTerms; j++)
            if (polyA[i] && polyB[j]) // 只计算非零项的乘积
                productResult[i + j] += polyA[i] * polyB[j];
}
 
// 输入多项式
void InputPolynomial(int* polynomial, int numTerms) {
    for (int i = 0; i < numTerms; i++) {
        int coefficient, exponent;
        cin >> coefficient >> exponent;
        polynomial[exponent] = coefficient; // 将系数存储到对应的指数位置
    }
}
 
// 输出多项式
void PrintPolynomial(int* polynomial) {
    bool hasOutput = false; // 用于判断是否有输出
    for (int i = 0; i < maxTermsPow2; i++) {
        if (polynomial[i]) {
            cout << polynomial[i] << " " << i << " ";
            hasOutput = true;
        }
    }
    if (!hasOutput) { // 如果没有输出，则输出0
        cout << "0 0";
    }
    cout << endl;
}
 
int main() {
    int numTerms;
 
    // 输入第一个多项式
    cin >> numTerms;
    InputPolynomial(polyA, numTerms);
 
    // 输入第二个多项式
    cin >> numTerms;
    InputPolynomial(polyB, numTerms);
 
    // 输入操作选择
    cin >> numTerms;
    switch (numTerms) {
        case 2: // 加法
        case 0: 
            AddPolynomials();
            PrintPolynomial(sumResult);
            if (numTerms == 0) break; // 如果选择为0，直接退出
        case 1: // 乘法
            MultiplyPolynomials();
            PrintPolynomial(productResult);
            break;
    }
 
    return 0;
}