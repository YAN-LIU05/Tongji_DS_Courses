/* 2352018 大数据 刘彦 */
#include <iostream>
#include <iomanip>
#include "17-b2-time.h"
using namespace std;

/* --- 给出Time类的成员函数的体外实现(含友元及其它必要的公共函数)  --- */

/***************************************************************************
  函数名称：
  功    能：构造函数
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
Time::Time()
{
	hour = 0;
	minute = 0;
	second = 0;
}

/***************************************************************************
  函数名称：
  功    能：三参构造函数
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
Time::Time(int h, int m, int s)
{
	this->set(h, m, s);
}

/***************************************************************************
  函数名称：
  功    能：int构造函数
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
Time::Time(int total_seconds)
{
	while (total_seconds < 0)
		total_seconds += 86400;
	total_seconds %= 86400;
	set(0, 0, 0);
	while (total_seconds >= 3600)
	{
		total_seconds -= 3600;
		++hour;
	}
	while (total_seconds >= 60)
	{
		total_seconds -= 60;
		++minute;
	}
	second = total_seconds;
}

/***************************************************************************
  函数名称：set
  功    能：
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
void Time::set(int h, int m, int s) 
{
	if (h >= 0 && h < 24 && m >= 0 && m < 60 && s >= 0 && s < 60) 
	{
		hour = h;
		minute = m;
		second = s;
	}
	else 
	{
		hour = 0;
		minute = 0;
		second = 0;
	}
}

/***************************************************************************
  函数名称：show
  功    能：
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
void Time::show()
{
	cout << setfill('0') << setw(2) << hour << ':';
	cout << setfill('0') << setw(2) << minute << ':';
	cout << setfill('0') << setw(2) << second;
	cout << endl;
}

/***************************************************************************
  函数名称：get
  功    能：
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
void Time::get(int& h, int& m, int& s)
{
	h = hour;
	m = minute;
	s = second;
}

/***************************************************************************
  函数名称：
  功    能：类型转换函数
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
Time::operator int() const
{
	int total_seconds = 0;
	int i = 0;
	while (i < hour)
	{
		total_seconds += 3600;
		i++;
	}
	i = 0;
	while (i < minute) 
	{
		total_seconds += 60;
		i++;
	}
	total_seconds += second;
	return total_seconds;
}

/***************************************************************************
  函数名称：
  功    能：
  输入参数：
  返 回 值：
  说    明：以下为重载运算符
***************************************************************************/
Time operator+(const Time& time, const int s)
{
	return Time((int)time + s);
}
Time operator+(const int s, const Time& time)
{
	return time + s;
}
int  operator -(const Time& time1, const Time& time2)
{
	return (int)time1 - (int)time2;
}
Time operator -(const Time& time, const int s)
{
	return Time((int)time - s);
}
Time& Time::operator++()
{
	int total_seconds = (int)*this;
	total_seconds++;
	*this = Time(total_seconds);
	return *this;
}
Time  Time::operator++(int)
{
	Time temp(this->hour, this->minute, this->second);
	int total_seconds = (int)*this;
	total_seconds++;
	*this = Time(total_seconds);
	return temp;
}
Time& Time::operator--()
{
	int total_seconds = (int)*this;
	total_seconds--;
	*this = Time(total_seconds);
	return *this;
}
Time  Time::operator--(int)
{
	Time temp(this->hour, this->minute, this->second);
	int total_seconds = (int)*this;
	total_seconds--;
	*this = Time(total_seconds);
	return temp;
}
ostream& operator<<(ostream& out, const Time& time)
{
	out << setfill('0') << setw(2) << time.hour << ':';
	out << setfill('0') << setw(2) << time.minute << ':';
	out << setfill('0') << setw(2) << time.second;
	return out;
}
istream& operator>>(istream& in, Time& time)
{
	int y, min, sec;
	in >> y >> min >> sec;
	time.set(y, min, sec);
	return in;
}
bool operator<(const Time& time1, const Time& time2)
{
	return (int)time1 < (int)time2;
}
bool operator>(const Time& time1, const Time& time2)
{
	return (int)time1 > (int)time2;
}
bool operator==(const Time& time1, const Time& time2)
{
	return (int)time1 == (int)time2;
}
bool operator!=(const Time& time1, const Time& time2)
{
	return (int)time1 != (int)time2;
}
bool operator>=(const Time& time1, const Time& time2)
{
	return (int)time1 >= (int)time2;
}
bool operator<=(const Time& time1, const Time& time2)
{
	return (int)time1 <= (int)time2;
}
