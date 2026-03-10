/* 2352018 大数据 刘彦 */
#pragma once

#include <iostream>
using namespace std;

/* 如果有其它全局函数需要声明，写于此处 */

/* 如果有需要的宏定义、只读全局变量等，写于此处 */

/* 补全Date类的定义，所有成员函数均体外实现，不要在此处体内实现 */
class Date {
private:
	int year;
	int month;
	int day;
	/* 不允许添加数据成员 */
    static bool is_leap_year(int year);
    static int days_in_month(int year, int month);
    void normalize();
public:
	/* 根据需要定义所需的成员函数、友元函数等(不允许添加数据成员) */
    Date();
    Date(int days);
    Date(int y, int m, int d);
    void set(int y);
    void set(int y, int m);
    void set(int y, int m, int d);
    void get(int& y, int& m, int& d) const;
    void show() const;
    
    operator int() const;
    Date& operator=(int days);

    Date& operator++();    // 前置++
    Date operator++(int);  // 后置++
    Date& operator--();    // 前置--
    Date operator--(int);  // 后置--

    friend Date operator+(const Date& date, int days);
    friend Date operator+(int days, const Date& date);
    friend Date operator-(const Date& date, int days);
    friend int operator-(const Date& lhs, const Date& rhs);

    friend bool operator==(const Date& lhs, const Date& rhs);
    friend bool operator!=(const Date& lhs, const Date& rhs);
    friend bool operator<(const Date& lhs, const Date& rhs);
    friend bool operator<=(const Date& lhs, const Date& rhs);
    friend bool operator>(const Date& lhs, const Date& rhs);
    friend bool operator>=(const Date& lhs, const Date& rhs);

    friend ostream& operator<<(ostream& os, const Date& date);
    friend istream& operator>>(istream& is, Date& date);
};

