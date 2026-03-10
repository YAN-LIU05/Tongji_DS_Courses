/* 2352018 信06 刘彦 */
#include <iostream>
using namespace std;

#define MAX_BINARY_LENGTH 32

unsigned int change(const char * num)
{
    unsigned int decimal = 0;

    while (*num) 
    { 
        decimal = decimal * 2 + *num - '0'; // 乘以2然后加上当前位的十进制值
        num++;
    }
    return decimal;
}

int main() 
{
    char num[MAX_BINARY_LENGTH + 1];
    unsigned int decimal;

    cout << "请输入一个0/1组成的字符串，长度不超过32" << endl;
    cin >> num; // 直接读取二进制字符串

    decimal = change(num); 

    cout << decimal << endl; 

    return 0;
}