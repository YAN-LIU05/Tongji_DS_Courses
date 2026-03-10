/* 2352018 大数据 刘彦 */
#pragma once

#include <iostream>
using namespace std;

/* 如果有其它全局函数需要声明，写于此处 */

/* Time类的声明 */
class Time {
protected:
	/* 除这三个以外，不允许再定义任何数据成员 */
	int hour;
	int minute;
	int second;
public:
	/* 允许需要的成员函数及友元函数的声明 */
	Time();
	Time(int h, int m, int s);
	Time(int total_seconds);
	void set(const int h = 0, const int m = 0, const int s = 0);
	void get(int& h, int& m, int& s);
	void show();
	operator int() const;

	Time& operator++();
	Time operator++(int);
	Time& operator--();
	Time operator--(int);
	/* 允许加入友元声明（如果有必要） */
	friend Time operator+(const Time& time, const int s);
	friend Time operator+(const int s, const Time& time);
	friend int operator-(const Time& time1, const Time& time2);
	friend Time operator-(const Time& time, const int s);
	friend ostream& operator<<(ostream& out, const Time& time);
	friend istream& operator>>(istream& in, Time& time);
	friend bool operator<(const Time& time1, const Time& time2);
	friend bool operator>(const Time& time1, const Time& time2);
	friend bool operator==(const Time& time1, const Time& time2);
	friend bool operator!=(const Time& time1, const Time& time2);
	friend bool operator>=(const Time& time1, const Time& time2);
	friend bool operator<=(const Time& time1, const Time& time2);
};