/* 2352018 大数据 刘彦 */
#pragma once

#include "17-b2-date.h"
#include "17-b2-time.h"

/* 如果有其它全局函数需要声明，写于此处 */

/* DateTime类的基本要求：
	1、不允许定义任何数据成员
	2、尽量少定义成员函数
*/

class DateTime :public Date, public Time {
protected:
	/* 不允许再定义任何数据成员 */

public:
	/* 不允许再定义任何数据成员，允许需要的成员函数及友元函数的声明 */
	DateTime();
	DateTime(int y, int mo, int d, int h, int m, int sec);
	DateTime(long long total_seconds);
	void set(long long total_seconds);
	void set(const int y = 1900, const int mo = 1, const int d = 1, const int h = 0, const int m = 0, const int s = 0);
	void get(int& y, int& mo, int& d, int& h, int& m, int& s) const;
	void show() const;
	operator long long() const;

	DateTime& operator ++();
	DateTime operator ++(int);
	DateTime& operator --();
	DateTime operator --(int);
	/* 允许加入友元声明（如果有必要） */
	friend DateTime operator+(const DateTime& datetime, long long s);
	friend DateTime operator+(long long s, const DateTime& datetime);
	friend DateTime operator+(const DateTime& datetime, int s);
	friend DateTime operator+(int s, const DateTime& datetime);
	friend long long operator-(const DateTime& datetime1, const DateTime& datetime2);
	friend DateTime operator-(const DateTime& datetime, long long s);
	friend DateTime operator-(const DateTime& datetime, int s);
	friend ostream& operator << (ostream& out, const DateTime& datatime1);
	friend istream& operator >> (istream& in, DateTime& datatime1);
	friend bool operator<(const DateTime& datatime1, const DateTime& datatime2);
	friend bool operator>(const DateTime& datatime1, const DateTime& datatime2);
	friend bool operator<=(const DateTime& datatime1, const DateTime& datatime2);
	friend bool operator>=(const DateTime& datatime1, const DateTime& datatime2);
	friend bool operator!=(const DateTime& datatime1, const DateTime& datatime2);
	friend bool operator==(const DateTime& datatime1, const DateTime& datatime2);
#if defined(__linux) || defined(__linux__)
	friend DateTime operator+(const DateTime& datetime, long int s);
	friend DateTime operator+(long int s, const DateTime& datetime);
	friend DateTime operator-(const DateTime& datetime, long int s);
#endif
};