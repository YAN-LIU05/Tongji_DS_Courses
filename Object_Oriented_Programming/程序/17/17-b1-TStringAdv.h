/* 2352018 大数据 刘彦 */
#pragma once

#include <climits>
#include "17-b1-TString.h"
using namespace std;

/* TStringAdv 类的定义 */
class TStringAdv : public TString {
protected:
	//friend const TStringAdv operator+(const TStringAdv& strl, const TStringAdv& str2);
	//friend const TStringAdv operator+(const TStringAdv& str, const char& c);
	//friend const TStringAdv operator+(const char& c, const TStringAdv& str);
public:
	// 构造函数
	TStringAdv();
	TStringAdv(const char* str);
	TStringAdv(const TString& str);
	TStringAdv(const TStringAdv& str);
	~TStringAdv();

	// 功能函数

	TStringAdv& assign(const TStringAdv& tstring);
	TStringAdv& assign(const char* str);
	//TStringAdv& assign(const char& c);

	TStringAdv& append(const TStringAdv& tstring);
	TStringAdv& append(const char* str);
	TStringAdv& append(const char& c);

	TStringAdv& insert(const TStringAdv& tstring, int pos);
	TStringAdv& insert(const char* str, int pos);
	TStringAdv& insert(const char& c, int pos);

	TStringAdv& erase(const TStringAdv& tstring);
	TStringAdv& erase(const char* s);
	TStringAdv& erase(const char& c);

	TStringAdv substr(const int pos, const int sublen = INT_MAX) const;

	char& at(const int n);

	friend int TStringAdvLen(const TStringAdv& str);


};

int TStringAdvLen(const TStringAdv& str);