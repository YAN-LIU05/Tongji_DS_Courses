/* 2352018 大数据 刘彦 */

/* 允许添加需要的头文件、宏定义等 */
#define _CRT_SECURE_NO_WARNINGS
#include <iostream>
#include <string.h>
#include "17-b1-TString.h"
#include "17-b1-TStringAdv.h"
using namespace std;

/* 给出 TStringAdv 类的所有成员函数的体外实现 */
TStringAdv::TStringAdv() : TString() 
{
}
TStringAdv::TStringAdv(const char* str) : TString(str) 
{
}
TStringAdv::TStringAdv(const TString& str) : TString(str) 
{
}
TStringAdv::TStringAdv(const TStringAdv& str) : TString(str) 
{
}
TStringAdv::~TStringAdv() 
{
}

const TStringAdv operator+(const TStringAdv& str1, const TStringAdv& str2) 
{
	return TStringAdv(TString(str1) + TString(str2));
}
const TStringAdv operator+(const TStringAdv& str, const char& c)
{
	return TString(str) + c;
}
const TStringAdv operator+(const char& c, const TStringAdv& str)
{
	return c + TString(str);
}

TStringAdv& TStringAdv::assign(const TStringAdv& tstring)
{
	if (this != &tstring)
		TString::operator=(tstring);
	return *this;
}
TStringAdv& TStringAdv::assign(const char* str)
{
	TString::operator=(str);
	return *this;
}
//TStringAdv& TStringAdv::assign(const char& c)
//{
//    if (c == '\0') 
//    {
//        delete[] content; 
//        len = 0; 
//        content = new(nothrow) char[len + 2];
//        my_exit(content);
//        content[0] = '\0'; 
//        return *this; 
//    }
//    char str[2] = { c, '\0' };
//    TStringAdv temp(str);
//    *this = temp; 
//    return *this; 
//}

TStringAdv& TStringAdv::append(const TStringAdv& other)
{
    *this += other;
    return *this;
}
TStringAdv& TStringAdv::append(const char* str)
{
    *this += str;
    return *this;
}
TStringAdv& TStringAdv::append(const char& c)
{
    if (c == '\0')
        return *this;
    len++;
    char* newstr = new(nothrow) char[len + 1];
    my_exit(newstr);
    memcpy(newstr, content, (len - 1) * sizeof(char));

    delete[]content;
    content = newstr;
    content[len - 1] = c;
    content[len] = '\0';
    return *this;
}

TStringAdv& TStringAdv::insert(const TStringAdv& tstring, int pos)
{
	if (pos < 1 || pos > len + 1)
		return *this;
	len = len + tstring.len;
	char* newstr = new(nothrow) char[len + 1];
	my_exit(newstr);
	memcpy(newstr, content, (pos - 1) * sizeof(char));
	memcpy(newstr + pos - 1, tstring.content, tstring.len * sizeof(char));
	memcpy(newstr + pos - 1 + tstring.len, content + pos - 1, (len - tstring.len - pos + 1) * sizeof(char));

	newstr[len] = '\0';
	delete[]content;
	content = newstr;
	return *this;
}
TStringAdv& TStringAdv::insert(const char* str, int pos)
{
	if (str == NULL || (pos < 1 || pos > len + 1) || strlen(str) == 0)
		return *this;
	len = len + strlen(str);
	char* newstr = new(nothrow) char[len + 1];
	my_exit(newstr);
	memcpy(newstr, content, (pos - 1) * sizeof(char));
	memcpy(newstr + pos - 1, str, strlen(str) * sizeof(char));
	memcpy(newstr + pos - 1 + strlen(str), content + pos - 1, (len - strlen(str) - pos + 1) * sizeof(char));
	newstr[len] = '\0';
	delete[]content;
	content = newstr;
	return *this;
}
TStringAdv& TStringAdv::insert(const char& c, int pos)
{
	if (pos < 1 || pos > len + 1)
		return *this;
	if (c == '\0')
	{
		len = pos - 1;
		char* newstr = new(nothrow) char[len + 1];
		my_exit(newstr);
		memcpy(newstr, content, (pos - 1) * sizeof(char));
		newstr[pos - 1] = '\0';
		delete[] content;
		content = newstr;
		return *this;
	}
	len = len + 1;
	char* newstr = new(nothrow) char[len + 1];
	my_exit(newstr);
	memcpy(newstr, content, (pos - 1) * sizeof(char));
	newstr[pos - 1] = c;
	memcpy(newstr + pos, content + pos - 1, (len - pos) * sizeof(char));
	newstr[len] = '\0';
	delete[] content;
	content = newstr;
	return *this;
}

TStringAdv& TStringAdv::erase(const TStringAdv& other)
{
	*this -= other;
	return *this;
}
TStringAdv& TStringAdv::erase(const char* str)
{
	*this -= str;
	return *this;
}
TStringAdv& TStringAdv::erase(const char& c)
{
	*this -= c;
	return *this;
}

TStringAdv TStringAdv::substr(const int pos, const int sublen) const
{
	int substr_len = sublen;
	if (pos < 1 || pos > len || sublen <= 0)
		return TStringAdv();

	if (sublen == INT_MAX || pos + sublen - 1 > len)
		substr_len = len - pos + 1;
	char* sub_content = new(nothrow) char[substr_len + 1];
	my_exit(sub_content);
	strncpy(sub_content, content + pos - 1, substr_len);
	sub_content[substr_len] = '\0';

	TStringAdv sub_string;
	sub_string.content = sub_content;
	sub_string.len = substr_len;
	return sub_string;
}

char& TStringAdv::at(const int n)
{
	return (*this)[n]; 
}

int TStringAdvLen(const TStringAdv& str)
{
	return TStringLen(str);
}
