/* 2352018 大数据 刘彦 */
#include <iostream>
#include <iomanip>
#include "16-b4.h"
using namespace std;

/* 给出 Date 类的所有成员函数的体外实现 */
#define BASE_YEAR 1900
#define MAX_YEAR 2099

bool Date::is_leap_year(int year)
{
    return (year % 4 == 0 && year % 100 != 0) || (year % 400 == 0);
}

int Date::days_in_month(int year, int month)
{
    static const int days[] = { 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 };
    if (month == 2 && is_leap_year(year)) return 29;
    return days[month - 1];
}

void Date::normalize()
{
    if (year < BASE_YEAR || year > MAX_YEAR)
        year = 2000;
    if (month < 1 || month > 12)
        month = 1;
    if (day < 1 || day > days_in_month(year, month))
        day = 1;
}

Date::Date()
{
    year = 2000;
    month = 1;
    day = 1;
}

Date::Date(int y, int m, int d)
{
    year = y;
    month = m;
    day = d;
    normalize();
}

void Date::set(int y)
{
    if (y != 0)
        year = y;
    month = 1;
    day = 1;
    normalize();
}

void Date::set(int y, int m)
{
    if (y != 0)
        year = y;
    if (m != 0)
        month = m;
    day = 1;
    normalize();
}

void Date::set(int y, int m, int d)
{
    if (y != 0)
        year = y;
    if (m != 0)
        month = m;
    if (d != 0)
        day = d;
    normalize();
}

void Date::get(int& y, int& m, int& d) const
{
    y = year;
    m = month;
    d = day;
}

void Date::show() const
{
    cout << year << "年" << month << "月" << day << "日" << endl;
}

Date::Date(int days)
{
    if (days <= 1)
    {
        year = BASE_YEAR;
        month = 1;
        day = 1;
    }
    else if (days >= 73049) // 大于等于73049，设置为2099.12.31
    {
        year = MAX_YEAR;
        month = 12;
        day = 31;
    }
    else // 正常计算日期
    {
        year = BASE_YEAR;
        month = 1;
        day = 1;
        while (days > 0)
        {
            int dim = days_in_month(year, month);
            if (days <= dim)
                break;
            days -= dim;
            if (++month > 12)
            {
                month = 1;
                ++year;
            }
        }
        day += days - 1;
    }
}

Date& Date::operator=(int days)
{
    *this = Date(days);
    return *this;
}

Date::operator int() const
{
    int days = 0;
    for (int y = BASE_YEAR; y < year; ++y)
        days += is_leap_year(y) ? 366 : 365;
    for (int m = 1; m < month; ++m)
        days += days_in_month(year, m);
    days += day;
    return days;
}

Date& Date::operator++()
{
    *this = *this + 1;
    return *this;
}

Date Date::operator++(int)
{
    Date temp = *this;
    ++(*this);
    return temp;
}

Date& Date::operator--()
{
    *this = *this - 1;
    return *this;
}

Date Date::operator--(int)
{
    Date temp = *this;
    --(*this);
    return temp;
}

Date operator+(const Date& date, int days)
{
    int total_days = int(date) + days;
    if (total_days < 1)
        total_days = 1;
    if (total_days > 73049)
        total_days = 73049;

    int y = BASE_YEAR, m = 1, d = 1;
    while (total_days > 0)
    {
        int dim = Date::days_in_month(y, m);
        if (total_days <= dim)
            break;
        total_days -= dim;
        if (++m > 12)
        {
            m = 1;
            ++y;
        }
    }
    d = total_days;
    return Date(y, m, d);
}

Date operator+(int days, const Date& date)
{
    return date + days;
}

Date operator-(const Date& date, int days)
{
    return date + (-days);
}

int operator-(const Date& lhs, const Date& rhs)
{
    return int(lhs) - int(rhs);
}

bool operator==(const Date& lhs, const Date& rhs)
{
    return int(lhs) == int(rhs);
}

bool operator!=(const Date& lhs, const Date& rhs)
{
    return !(lhs == rhs);
}

bool operator<(const Date& lhs, const Date& rhs)
{
    return int(lhs) < int(rhs);
}

bool operator<=(const Date& lhs, const Date& rhs)
{
    return int(lhs) <= int(rhs);
}

bool operator>(const Date& lhs, const Date& rhs)
{
    return int(lhs) > int(rhs);
}

bool operator>=(const Date& lhs, const Date& rhs)
{
    return int(lhs) >= int(rhs);
}

ostream& operator<<(ostream& os, const Date& date)
{
    os << date.year << "年" << date.month << "月" << date.day << "日";
    return os;
}

istream& operator>>(istream& is, Date& date)
{
    int y, m, d;
    is >> y >> m >> d;
    date.set(y, m, d);
    return is;
}

/* 如果有需要的其它全局函数的实现，可以写于此处 */