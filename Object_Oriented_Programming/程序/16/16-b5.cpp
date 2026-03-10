/* 2352018 大数据 刘彦 */

/* 允许添加需要的头文件、宏定义等 */
#define _CRT_SECURE_NO_WARNINGS
#include <iostream>
#include <string.h>
#include "16-b5.h"
using namespace std;

/* 给出 TString 类的所有成员函数的体外实现 */
TString::TString()
{
    len = 0;  // 初始化长度为0
    content = new(nothrow) char[len + 1];  // 分配内存，使用 'nothrow' 防止抛出异常
    my_exit(content);
    content[0] = '\0';  // 将第一个字符设置为 '\0'，表示空字符串
}

TString::TString(const char* str)
{
    len = (str == nullptr) ? 0 : strlen(str);  // 计算字符串的长度，如果 s 为 nullptr，则长度为 0

    // 使用 new 分配内存，并在分配失败时返回 nullptr
    content = new(nothrow) char[len + 1];

    my_exit(content);

    if (str == nullptr)
        content[0] = '\0';  // 如果 s 为 nullptr，将 content 初始化为空字符串
    else
        strcpy(content, str);  // 复制 s 的内容到 content
}

TString::TString(const TString& other)
{
    len = other.len;  // 复制长度
    content = new(nothrow) char[len + 1];  // 使用 'new' 分配内存

    my_exit(content);

    strcpy(content, other.content);  // 复制内容
}

TString::~TString()
{
    len = 0;
    delete[]content;
}

char* TString::c_str() const
{
    return content;
}

TString& TString::operator= (const TString& other)
{
    if (this != &other)
    {
        delete[]content;
        len = other.len;
        content = new(nothrow) char[len + 1]; 

        my_exit(content);
        strcpy(content, other.content);
    }
    return *this;
}

ostream& operator<< (ostream& out, const TString& str) 
{
    if (str.len == 0)
        out << "<EMPTY>";
    else
        out << str.content;
    return out;
}

istream& operator>> (istream& in, TString& str)
{
    char temp[2048] = { '\0' };
    in >> temp;
    str.len = strlen(temp);
    delete[]str.content;
    str.content = new(nothrow) char[str.len + 1];

    my_exit(str.content);
    strcpy(str.content, temp);
    return in;
}

const TString operator+(const TString& str1, const TString& str2) 
{
    TString temp;
	temp.len = str1.len + str2.len;
    temp.content = new(nothrow) char[str1.len + str2.len + 1];
    my_exit(temp.content);

    temp.copy_strings(temp.content, str1.content, str1.len, str2.content, str2.len);
    return temp;
}

const TString operator+(const TString& str1, const char* str2) 
{
    TString temp;
    int str2_len = (str2 != nullptr) ? strlen(str2) : 0;
	temp.len = str1.len + str2_len;
    temp.content = new(nothrow) char[str1.len + str2_len + 1];
    my_exit(temp.content);
    temp.copy_strings(temp.content, str1.content, str1.len, str2, str2_len);
    return temp;
}

const TString operator+(const char c, const TString & str) 
{
    TString temp;
	temp.len = str.len + 1;
    temp.content = new(nothrow) char[str.len + 1 + 1];
    my_exit(temp.content);
    temp.content[0] = c;
    temp.copy_strings(temp.content + 1, str.content, str.len, "", 0);

    return temp;
}

const TString operator+(const TString& str, const char c)
{
    TString temp;
	temp.len = str.len + 1;
    temp.content = new(nothrow) char[str.len + 1 + 1];
    my_exit(temp.content);
	memcpy(temp.content, str.content, str.len * sizeof(char));
	temp.content[temp.len - 1] = c;
	temp.content[temp.len] = '\0';

    return temp;
}

TString& TString::operator+=(const TString& other) 
{
    append_to_content(other.content, other.len);
    return *this;
}

TString& TString::operator+=(const char* s) 
{
    if (s) 
        append_to_content(s, strlen(s));
    return *this;
}

TString& TString::operator+=(const char c) 
{
    char temp[2] = { c, '\0' };  // 用临时字符串
    append_to_content(temp, 1);
    return *this;
}

TString operator-(const TString& str1, const TString& str2) 
{
	// 查找 str2 在 str1 中的位置
	int* tmp = new (std::nothrow) int[str2.len];
	if (tmp == nullptr)
	{
		cerr << "内存分配失败" << endl;
		exit(-1); 
	}

	memset(tmp, 0, sizeof(int) * str2.len);

	// 构建 tmp 数组
	int i = 1, j = 0;
	while (i < str2.len)
	{
		if (str2.content[i] == str2.content[j])
			tmp[i++] = ++j;
		else
		{
			if (j != 0)
				j = tmp[j - 1];
			else
				tmp[i++] = 0;
		}
	}

	// 匹配过程
	i = 0, j = 0;
	int locate = -1;
	while (i < str1.len)
	{
		if (str1.content[i] == str2.content[j]) 
		{
			++i;
			++j;
		}
		if (j == str2.len) 
		{
			locate = i - j;  // 找到完全相同的子串，记录其起始位置
			break;
		}
		else if (i < str1.len && str1.content[i] != str2.content[j]) 
		{
			if (j != 0)
				j = tmp[j - 1];
			else
				++i;
		}
	}

	delete[] tmp;

	if (locate == -1)
		return str1;

	// 创建新的 TString 对象 temp
	TString temp;

	temp.len = str1.len - str2.len;
	temp.content = new char[str1.len - str2.len + 1];
	my_exit(temp.content);

	// 复制 str1 中去掉子串后的内容到 temp.content
	for (int i = 0; i < locate; i++) 
		temp.content[i] = str1.content[i];  // 将 str1 中 locate 之前的内容复制到 temp 中

	for (int i = locate, j = locate + str2.len; j < str1.len; i++, j++) 
		temp.content[i] = str1.content[j];  // 复制去除子串后的剩余内容

	temp.content[str1.len - str2.len] = '\0';  // 保证字符串结束符

	return temp;
}

TString operator-(const TString& str1, const char c) 
{
	char str2[2] = { c, '\0' };

	// 查找字符 c 在 str1 中的位置
	int length = str1.len;

	int* tmp = new (std::nothrow) int[1];
	if (tmp == nullptr)
		exit(-1);  // 内存分配失败，退出程序

	// 初始化 tmp 数组
	tmp[0] = 0;

	int i = 0, j = 0;
	int locate = -1;
	while (i < length) 
	{
		if (str1.content[i] == str2[j]) 
		{
			++i;
			++j;
		}
		if (j == 1) 
		{
			locate = i - j;  // 找到字符的位置
			break;
		}
		else if (i < length && str1.content[i] != str2[j]) 
		{
			if (j != 0)
				j = tmp[j - 1];
			else
				++i;
		}
	}

	delete[] tmp;

	if (locate == -1)
		return str1;

	// 创建新的 TString 对象 temp
	TString temp;
	temp.len = str1.len - 1;

	// 手动分配内存
	temp.content = new char[temp.len + 1];
	if (temp.content == nullptr)
		exit(-1);  // 内存分配失败，退出程序

	// 复制 str1 中去掉字符后的内容到 temp.content
	for (int i = 0; i < locate; i++)
		temp.content[i] = str1.content[i];

	for (int i = locate; str1.content[i + 1] != '\0'; i++)
		temp.content[i] = str1.content[i + 1];

	temp.content[temp.len] = '\0';  // 保证字符串结束符

	return temp;
}

TString& TString::operator-=(const TString& str)
{
	if (str.len == 0 || len < str.len)
		return *this;

	// 构建部分匹配表
	int* tmp = new (std::nothrow) int[str.len];
	if (tmp == nullptr)
	{
		std::cerr << "内存分配失败" << std::endl;
		exit(-1);
	}
	memset(tmp, 0, sizeof(int) * str.len);

	int i = 1, j = 0;
	while (i < str.len) {
		if (str.content[i] == str.content[j]) 
			tmp[i++] = ++j;
		else if (j != 0) 
			j = tmp[j - 1];
		else 
			tmp[i++] = 0;
	}

	// 搜索子字符串
	i = 0, j = 0;
	int locate = -1; // 子串位置
	while (i < len) {
		if (content[i] == str.content[j]) 
		{
			i++;
			j++;
		}
		if (j == str.len) 
		{
			locate = i - j; // 找到子串起始位置
			break;
		}
		else if (i < len && content[i] != str.content[j]) 
		{
			if (j != 0) 
				j = tmp[j - 1];
			else 
				i++;
		}
	}
	delete[] tmp;

	// 如果未找到，返回原字符串
	if (locate == -1)
		return *this;

	// 删除子串
	len -= str.len;
	char* temp = nullptr;
	temp = new(nothrow) char[len + 1];
	my_exit(temp);

	for (int k = 0; k < locate; k++)
		temp[k] = content[k];
	for (int k = locate; content[k + str.len] != '\0'; k++)
		temp[k] = content[k + str.len];

	delete[] content;
	content = temp;
	content[len] = '\0';
	return *this;
}

TString& TString::operator-=(const char c)
{
	char str2[2] = { c, '\0' };
	TString temp(str2);
	return (*this -= temp);
}

TString TString::operator*(int n) const 
{
	if (n <= 0) 
		return TString("");  // 返回空字符串

	TString temp;  // 创建一个空的字符串
	for (int i = 0; i < n; i++) 
		temp += *this;  // 将原字符串追加到 temp 中
	return temp;
}

TString& TString::operator*=(const int n)
{
	if (n <= 0)	// 如果 n <= 0，直接清空字符串
	{
		TString empty;
		*this = empty;
		return *this;
	}

	// 分配新的内存空间
	char* new_content = new char[len * n + 1];

	// 将原字符串重复 n 次填充到 new_content
	for (int i = 0; i < n; ++i)
		strcpy(new_content + i * len, content);

	// 释放原有内存并更新 content 和 len
	delete[] content;
	content = new_content;
	len = len * n;

	return *this;
}

TString TString::operator!() // 自己不被翻转，所以返回临时变量
{
	TString temp = *this;
	temp.content = new(nothrow) char[len + 1];
	my_exit(temp.content);
	for (int i = 0; i < len; i++)
		temp.content[i] = content[len - i - 1];
	temp.content[len] = '\0';
	return temp; // 自己不被翻转，所以返回临时变量
}

bool operator<(const TString& str1, const TString& str2) 
{
	return strcmp(str1.content ? str1.content : "", str2.content ? str2.content : "") < 0;
}

bool operator>(const TString& str1, const TString& str2) 
{
	return strcmp(str1.content ? str1.content : "", str2.content ? str2.content : "") > 0;
}

bool operator<=(const TString& str1, const TString& str2) 
{
	return strcmp(str1.content ? str1.content : "", str2.content ? str2.content : "") <= 0;
}

bool operator>=(const TString& str1, const TString& str2) 
{
	return strcmp(str1.content ? str1.content : "", str2.content ? str2.content : "") >= 0;
}

bool operator==(const TString& str1, const TString& str2) 
{
	return strcmp(str1.content ? str1.content : "", str2.content ? str2.content : "") == 0;
}

bool operator!=(const TString& str1, const TString& str2) 
{
	return strcmp(str1.content ? str1.content : "", str2.content ? str2.content : "") != 0;
}

char& TString::operator[](const int n)
{
	return content[n];
}

void TString::append(const TString& other) 
{
	*this += other;
}

TString& TString::append(const char* str) 
{
	*this += str;
	return *this;
}

TString& TString::append(const char c) 
{
	*this += c;
	return *this;
}

int TString::length()
{
	return len;
}
int TStringLen(const TString& str)
{
	return str.len;
}

void TString::copy_strings(char* dest, const char* src1, int len1, const char* src2, int len2)
{
    // 使用 memcpy 合并两个字符串
    memcpy(dest, src1, len1 * sizeof(char));
    memcpy(dest + len1, src2, len2 * sizeof(char));
    dest[len1 + len2] = '\0';  // 确保目标字符串以 '\0' 结尾
}

void TString::append_to_content(const char* append_str, int append_len) 
{
    int old_len = len;
    len += append_len;

    // 分配新内存
    char* new_content = new (nothrow) char[len + 1];
    my_exit(new_content);

    // 复制旧数据和追加的新数据
    if (content) 
    {
        memcpy(new_content, content, old_len * sizeof(char));
        delete[] content;
    }
    memcpy(new_content + old_len, append_str, append_len * sizeof(char));

    // 更新 content
    content = new_content;
    content[len] = '\0';
}

/* 如果有需要的其它全局函数的实现，可以写于此处 */
void my_exit(char* &content)
{
    if (!content)  // 检查内存分配是否成功
    {
        cerr << "内存分配失败" << endl;
        exit(-1);  //程序终止
    }
}

