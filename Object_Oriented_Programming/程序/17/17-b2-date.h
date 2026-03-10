/* 2352018 大数据 刘彦 */
#pragma once

#include <iostream>
using namespace std;

/* 如果有其它全局函数需要声明，写于此处 */

/* Date类的声明 */
class Date {
protected:
	/* 除这三个以外，不允许再定义任何数据成员 */
	int year;
	int month;
	int day;
public:
	/* 允许需要的成员函数及友元函数的声明 */
	Date();                                      // 默认构造函数
	Date(const int y, const int m, const int d); // 三参构造函数
	Date(int total_days); // 转换构造函数，int->Date
	void set(const int y = 2000, const int m = 1, const int d = 1); // set成员函数
	void get(int& y, int& m, int& d);
	void show();

	Date& operator++();
	Date operator++(int);
	Date& operator--();
	Date operator--(int);
	bool operator<(const Date& date);
	bool operator>(const Date& date);
	bool operator==(const Date& date);
	operator int() const;  // 类型转换函数，将Date对象转化为int类型的天数
	/* 允许加入友元声明（如果有必要） */
	friend Date operator+(const Date& date, const int a);
	friend Date operator+(const int a, const Date& date);
	friend Date operator-(const Date& date, const int a);
	friend int operator-(const Date& date1, const Date& date2);
	friend ostream& operator<<(ostream& out, const Date& date);
	friend istream& operator>>(istream& in, Date& date);
	friend bool operator!=(const Date& date1, const Date& date2);
	friend bool operator>=(const Date& date1, const Date& date2);
	friend bool operator<=(const Date& date1, const Date& date2);
};