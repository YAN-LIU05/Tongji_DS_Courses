/* 2352018 大数据 刘彦 */
#pragma once

#include <iostream>
using namespace std;

enum week { sun, mon, tue, wed, thu, fri, sat };

/* 允许添加相应的函数声明 */
ostream& operator<<(ostream& os, const week& w);
istream& operator>>(istream& is, week& w);
week& operator++(week& w);
week operator++(week& w, int);
week& operator--(week& w);
week operator--(week& w, int);
week operator+(week w, int n);
week operator-(week w, int n);
week& operator+=(week& w, int n);
week& operator-=(week& w, int n);
char my_tolower(char c);