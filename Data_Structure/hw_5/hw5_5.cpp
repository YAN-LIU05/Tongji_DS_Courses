#include <iostream>
#include <cmath>
 
using namespace std;
 
// 判断一个数是否为素数
long long int signded(int n) {
    if (n % 2 == 0) {
        return -1;
    }
    return 1;
}
 
bool isPrime(int n) {
    if (n <= 1) return false;
    for (int i = 2; i <= sqrt(n); ++i) {
        if (n % i == 0) return false;
    }
    return true;
}
 
// 找到大于P的最小素数
int nextPrime(int P) {
    while (!isPrime(P)) {
        ++P;
    }
    return P;
}
 
// 计算字符串的哈希值
unsigned long long int hashFunction(const string& key) {
    unsigned long long int hashValue = 0;
    for (char ch : key) {
        hashValue = hashValue * 37 + ch;  // 每个字符按其ASCII值计算哈希
    }
    return hashValue;
}
 
int main() {
    int N, P;
    cin >> N >> P;
 
    // 如果P不是素数，找到大于P的最小素数作为哈希表大小
    if (!isPrime(P)) {
        P = nextPrime(P);
    }
 
    // 初始化哈希表，值设为-1表示该位置为空
    long long int* hashTable = new long long int[P];
    for (int i = 0; i < P; ++i) {
        hashTable[i] = -1;
    }
 
    // 输入N个名字
    string* names = new string[N];
    for (int i = 0; i < N; ++i) {
        cin >> names[i];
    }
 
    // 处理每个名字
    for (int i = 0; i < N; ++i) {
        unsigned long long int hashValue = hashFunction(names[i]);
        long long int idx = hashValue % P;  // 对P取模，映射到表内位置
        long long int probeCount = 0;  // 探测次数
        bool inserted = false;
 
        // 使用平方探测法解决冲突
        while (probeCount < P) {
            long long int increment = (probeCount + 1) / 2;
            long long int newIdx = idx + increment * increment * signded(probeCount);
            if (newIdx < 0 || newIdx >= P) {
                newIdx = (newIdx % P + P) % P;  // 处理越界情况
            }
            if (hashTable[newIdx] == -1) {
                hashTable[newIdx] = i;  // 插入位置
                cout << newIdx << " ";  // 输出的是1-based索引
                inserted = true;
                break;
            }
            ++probeCount;
        }
 
        // 如果没有找到插入位置
        if (!inserted) {
            cout << "- ";
        }
    }
 
    cout << endl;
 
    // 释放内存
    delete[] hashTable;
    delete[] names;
 
    return 0;
}