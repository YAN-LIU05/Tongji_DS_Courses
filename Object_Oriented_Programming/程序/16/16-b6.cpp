/* 2352018 大数据 刘彦 */

/* 允许添加需要的头文件、宏定义等 */
#define _CRT_SECURE_NO_WARNINGS
#include <iostream>
#include <sstream>
#include <cstring>
#include "16-b6.h"
using namespace std;

/* 给出 enum class week 类的所有成员函数的体外实现 */
ostream& operator<<(ostream& os, const week& w) 
{
    switch (w) 
    {
        case week::sun: 
            os << "星期日"; break;
        case week::mon: 
            os << "星期一"; break;
        case week::tue: 
            os << "星期二"; break;
        case week::wed: 
            os << "星期三"; break;
        case week::thu: 
            os << "星期四"; break;
        case week::fri: 
            os << "星期五"; break;
        case week::sat: 
            os << "星期六"; break;
        default: 
            os << "错误"; break;
    }
    return os;
}

istream& operator>>(istream& is, week& w) 
{
    char input[1024];  // 假设输入字符串的长度不会超过 1024 个字符
    is >> input;

    // 将输入转化为小写字母进行比较
    for (int i = 0; input[i] != '\0'; ++i) 
        input[i] = my_tolower(input[i]);

    if (strcmp(input, "sun") == 0) 
        w = week::sun;
    else if (strcmp(input, "mon") == 0) 
        w = week::mon;
    else if (strcmp(input, "tue") == 0) 
        w = week::tue;
    else if (strcmp(input, "wed") == 0) 
        w = week::wed;
    else if (strcmp(input, "thu") == 0) 
        w = week::thu;
    else if (strcmp(input, "fri") == 0) 
        w = week::fri;
    else if (strcmp(input, "sat") == 0) 
        w = week::sat;
    else 
        w = static_cast<week>(10); //一个错误值

    return is;
}

week& operator++(week& w) 
{
    w = static_cast<week>((static_cast<int>(w) + 1) % 7);
    return w;
}

week operator++(week& w, int) 
{
    week old = w;
    ++w;
    return old;
}

week& operator--(week& w) 
{
    w = static_cast<week>((static_cast<int>(w) + 6) % 7);
    return w;
}

week operator--(week& w, int) 
{
    week old = w;
    --w;
    return old;
}

week operator+(week w, int n) 
{
    int new_day = (static_cast<int>(w) + n) % 7;
    if (new_day < 0) 
        new_day += 7;  // 处理负数结果，确保在范围内
    return static_cast<week>(new_day);
}

week operator-(week w, int n) 
{
    int new_day = (static_cast<int>(w) - n) % 7;
    if (new_day < 0) 
        new_day += 7;  // 处理负数结果，确保在范围内
    return static_cast<week>(new_day);
}

week& operator+=(week& w, int n) 
{
    w = w + n;
    return w;
}

week& operator-=(week& w, int n)
{
    w = w - n;
    return w;
}

char my_tolower(char c) 
{
    if (c >= 'A' && c <= 'Z') 
        return c + ('a' - 'A');
    return c;
}