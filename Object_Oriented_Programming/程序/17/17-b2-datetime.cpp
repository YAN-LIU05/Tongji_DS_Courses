/* 2352018 大数据 刘彦 */
#include <iostream>
#include <iomanip>
#include "17-b2-datetime.h"
using namespace std;

/* --- 给出DateTime类的成员函数的体外实现(含友元及其它必要的公共函数)  --- */

/***************************************************************************
  函数名称：
  功    能：构造函数
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
DateTime::DateTime() : Date(), Time()
{
}

/***************************************************************************
  函数名称：
  功    能：三参构造函数
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
DateTime::DateTime(int y, int mo, int d, int h, int m, int s) 
{
	this->set(y, mo, d, h, m, s);
}

/***************************************************************************
  函数名称：
  功    能：long long构造函数
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
DateTime::DateTime(long long total_seconds)
{
	while (total_seconds < 0)
		total_seconds += 6311433600;
	total_seconds %= 6311433600;
	int y, mo, d, h, m, s;
	Date nowday((int)(total_seconds / 86400LL));
	Time nowtime((int)(total_seconds % 86400LL));
	nowday.get(y, mo, d);
	nowtime.get(h, m, s);
	(*this) = DateTime(y, mo, d, h, m, s);
}

/***************************************************************************
  函数名称：set
  功    能：
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
void DateTime::set(long long total_seconds)
{
	if (total_seconds < 0 || total_seconds >= 6311433600)
		(*this) = DateTime();
	else
		(*this) = DateTime(total_seconds);
}
void DateTime::set(int y, int m, int d, int hou, int min, int sec)
{
	year = 1900;
	month = 1;
	day = 1;
	hour = 0;
	minute = 0;
	second = 0;
	if (hou < 0 || hou >= 24 || min < 0 || min >= 60 || sec < 0 || sec >= 60 || y < 1900 || y > 2099 || m < 1 || m > 12 || d < 1) 
		return; 

	static const int days_in_month[] = { 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 };
	int max_day = days_in_month[m - 1];
	if (m == 2 && ((y % 4 == 0 && y % 100 != 0) || (y % 400 == 0))) 
		max_day = 29; // 闰年2月
	if (d < 1 || d > max_day) 
		return; // 日不合法，直接返回默认值

	// 所有合法时赋值
	year = y;
	month = m;
	day = d;
	hour = hou;
	minute = min;
	second = sec;
}

/***************************************************************************
  函数名称：get
  功    能：
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
void DateTime::get(int& y, int& mo, int& d, int& h, int& m, int& s) const
{
	y = year;
	mo = month;
	d = day;
	h = hour;
	m = minute;
	s = second;
}

/***************************************************************************
  函数名称：show
  功    能：
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
void DateTime::show() const
{
	cout << Date(year, month, day) << " " << Time(hour, minute, second) << endl;
}

/***************************************************************************
  函数名称：
  功    能：类型转换函数
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
DateTime::operator long long() const
{
	long long total_seconds = 0;
	total_seconds = ((int)Date(year, month, day) * 86400LL) + (long long)((int)Time(hour, minute, second));
	return total_seconds;
}

/***************************************************************************
  函数名称：
  功    能：
  输入参数：
  返 回 值：
  说    明：以下为重载运算符
***************************************************************************/
DateTime operator+(const DateTime& datetime, long long s)
{
	return DateTime((long long)datetime + s);
}
DateTime operator+(long long s, const DateTime& datetime)
{
	return datetime + s;
}
DateTime operator+(const DateTime& datetime, int s)
{
	return DateTime((long long)datetime + s);
}
DateTime operator+(int s, const DateTime& datetime)
{

	return datetime + s;
}
long long operator-(const DateTime& datetime1, const DateTime& datetime2)
{
	return (long long)datetime1 - (long long)datetime2;
}
DateTime operator-(const DateTime& datetime, long long s)
{
	return DateTime((long long)datetime - s);
}
DateTime operator-(const DateTime& datetime, int s)
{
	return DateTime((long long)datetime - s);
}
#if defined(__linux) || defined(__linux__)
DateTime operator+(const DateTime& datetime, long int s)
{
	return DateTime((long long)datetime + s);
}
DateTime operator+(long int s, const DateTime& datetime)
{
	return datetime + s;
}
DateTime operator-(const DateTime& datetime, long int s)
{
	return DateTime((long long)datetime - s);
}
#endif
DateTime& DateTime::operator++()
{
	long long total_seconds = (long long)(*this) + 1;
	total_seconds %= 6311433600;
	set(total_seconds);
	return *this;
}
DateTime DateTime::operator++(int)
{
	DateTime temp = (*this);
	long long total_seconds = (long long)(*this) + 1;
	total_seconds %= 6311433600;
	set(total_seconds);
	return temp;
}
DateTime& DateTime::operator--()
{
	long long total_seconds = (long long)(*this) - 1;
	while (total_seconds < 0)
		total_seconds += 6311433600;
	total_seconds %= 6311433600;
	set(total_seconds);
	return *this;
}
DateTime DateTime::operator--(int)
{
	DateTime temp = (*this);
	long long total_seconds = (long long)(*this) - 1;
	while (total_seconds < 0)
		total_seconds += 6311433600;
	total_seconds %= 6311433600;
	set(total_seconds);
	return temp;
}
ostream& operator<<(ostream& out, const DateTime& datatime)
{
	out << Date(datatime.year, datatime.month, datatime.day) << " " << Time(datatime.hour, datatime.minute, datatime.second);
	return out;
}
istream& operator >> (istream& in, DateTime& datatime)
{
	int y, mo, d, h, m, s;
	in >> y >> mo >> d >> h >> m >> s;
	datatime.set(y, mo, d, h, m, s);
	return in;
}
bool operator<(const DateTime& datatime1, const DateTime& datatime2)
{
	if (datatime1.year != datatime2.year)
		return datatime1.year < datatime2.year;
	if (datatime1.month != datatime2.month)
		return datatime1.month < datatime2.month;
	if (datatime1.day != datatime2.day)
		return datatime1.day < datatime2.day;
	if (datatime1.hour != datatime2.hour)
		return datatime1.hour < datatime2.hour;
	if (datatime1.minute != datatime2.minute)
		return datatime1.minute < datatime2.minute;
	return datatime1.second < datatime2.second;
}
bool operator>(const DateTime& datatime1, const DateTime& datatime2)
{
	return datatime2 < datatime1; // 直接复用小于运算符
}
bool operator<=(const DateTime& datatime1, const DateTime& datatime2)
{
	return !(datatime2 < datatime1); // 非大于即小于等于
}
bool operator>=(const DateTime& datatime1, const DateTime& datatime2)
{
	return !(datatime1 < datatime2); // 非小于即大于等于
}
bool operator!=(const DateTime& datatime1, const DateTime& datatime2)
{
	return (datatime1 < datatime2) || (datatime2 < datatime1); // 若两者不相等，则必定有一方小于另一方
}
bool operator==(const DateTime& datatime1, const DateTime& datatime2)
{
	return !(datatime1 != datatime2); // 非不等即相等
}