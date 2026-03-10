/* 2352018 大数据 刘彦 */

#pragma once

#include <iostream>
using namespace std;

/* 补全TString类的定义，所有成员函数均体外实现，不要在此处体内实现 */
class TString {
private:
	char* content;
	int   len;
	/* 根据需要定义所需的数据成员、成员函数、友元函数等 */
	void copy_strings(char* dest, const char* src1, int len1, const char* src2, int len2);
	void append_to_content(const char* appendStr, int appendLen);
public:
	/* 根据需要定义所需的数据成员、成员函数、友元函数等 */

	/* 构造函数 */
	TString();                                                           // 默认构造函数
	~TString();                                                          // 析构函数
	TString(const char* str);                                            // 一参构造函数
	TString(const TString& other);                                       // 一参构造函数
	char* c_str() const;                                                 // 复制构造函数
	
	/* 重载运算符 */
	TString& operator= (const TString& other);                           // 重载=
	
	friend ostream& operator<< (ostream& out, const TString& str);       // 重载<<
	friend istream& operator>> (istream& in, TString& str);              // 重载>>
	
	friend const TString operator+(const TString& str1, const TString& str2);// 第一个加法运算符重载：TString + TString
	friend const TString operator+(const TString& str1, const char* str2);   // 第二个加法运算符重载：TString + const char*
    friend const TString operator+(const char c, const TString& str);      // 第三个加法运算符重载：char + TString
	friend const TString operator+(const TString& str, const char c);      // 第四个加法运算符重载：TString + char

	TString& operator+=(const TString& other);                         // 第一个加赋值运算符重载：TString
	TString& operator+=(const char* str);                                // 第二个加赋值运算符重载：const char* 
	TString& operator+=(const char c);                                 // 第三个加赋值运算符重载：char  
	 
	friend TString operator-(const TString& str1, const TString& str2);    // 第一个减法运算符重载：TString - TString
	friend TString operator-(const TString& str1, const char c);         // 第二个减法运算符重载：TString - char

	TString& operator-=(const TString& str);                             // 第一个减赋值运算符重载：TString
	TString& operator-=(const char c);                                 // 第二个减赋值运算符重载：char  

	TString operator*(int n) const;                                    // 重载*  

	TString& operator*=(const int n);                                  // 重载*=

	TString operator!();                                               // 重载!

	friend bool operator<(const TString& str1, const TString& str2);       // 重载<
	friend bool operator>(const TString& str1, const TString& str2);       // 重载>
	friend bool operator<=(const TString& str1, const TString& str2);      // 重载<=
	friend bool operator>=(const TString& str1, const TString& str2);      // 重载>=
	friend bool operator==(const TString& str1, const TString& str2);      // 重载==
	friend bool operator!=(const TString& str1, const TString& str2);      // 重载!=

	char& operator[](const int n);                                     // 重载[]

	/* 操作函数 */
	void append(const TString& other);
	TString& append(const char c);
	TString& append(const char* str);
	int length();
	friend int TStringLen(const TString& str);
};

/* 如果有其它全局函数需要声明，写于此处 */
void my_exit(char*& content);                                                //内存分配检测函数
/* 如果有需要的宏定义、只读全局变量等，写于此处 */
