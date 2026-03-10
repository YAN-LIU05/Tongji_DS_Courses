/* 2352018 信06 刘彦 */
#include <iostream>
#include <cstdio>
using namespace std;

#define MAX_LEN 81

// 函数用于判断字符串是否是回文串
bool fun(char * str) 
{
    char * left = str, * right = str;
    while (* right)
        right++;
    right--; // 指向字符串最后一个字符

    while (left < right)   // 跳过空格
    {
        
        while (* left == ' ') 
            left++;
        while (* right == ' ') 
            right--;

        if (*left != *right) 
        {
            return false;
        }
        left++;
        right--;
    }
    return true;
}

int main() 
{
    char str[MAX_LEN];
    char * p = str;

    cout << "请输入一个长度小于80的字符串（回文串）" << endl;
    fgets(p, MAX_LEN, stdin); // 使用fgets读取字符串

    // 去除fgets读取的最后一个换行符
    char * end = p;
    while (* end) 
        end++;
    if (end > p && * (end - 1) == '\n') 
    {
        * (end - 1) = '\0';
    }

    if (fun(p)) 
    {
        cout << "yes" << endl;
    }
    else 
    {
        cout << "no" << endl;
    }

    return 0;
}