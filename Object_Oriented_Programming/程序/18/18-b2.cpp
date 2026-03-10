/* 2352018 大数据 刘彦 */
#include <iostream>
#include <cmath>
using namespace std;

/* 从此处到标记替换行之间，给出各种类的定义及实现
	1、不允许定义全局变量（不含const和#define）
	2、不允许添加其它系统头文件
*/
//自定义字符串复制函数
int tj_strcpy(char s1[], const char s2[])
{
	int i = 0; // 初始化索引变量i
	// 复制s2到s1，直到遇到空字符
	while (s2[i] != '\0')
	{
		s1[i] = s2[i];
		i++;
	}
	// 在s1的末尾添加空字符
	s1[i] = '\0';
	return 0; 
}
//此处给出三个类的定义及实现
class integral {
protected:
	double min, max;
	int    num;
	char   name[128];
public:
	virtual double value();
	friend istream& operator >>(istream& in, integral& _integral);
};
class integral_sin : public integral{
public:
	integral_sin();
	virtual double value();
};
class integral_cos : public integral {
public:
	integral_cos();
	virtual double value();
};
class integral_exp : public integral {
public:
	integral_exp();
	virtual double value();
};
//函数名称
integral_sin::integral_sin()
{
	tj_strcpy(name, "sinxdx");
}
integral_cos::integral_cos()
{
	tj_strcpy(name, "cosxdx");
}
integral_exp::integral_exp()
{
	tj_strcpy(name, "e^xdx");
}
//积分计算函数
double integral::value() 
{
	return 0;
}
double integral_sin::value()
{
	double result = 0;
	double width = (max - min) / num;
	for (int i = 1; i <= num; i++)
		result += sin(min + i * width) * width;
	cout << name << "[" << min << "~" << max << "/n=" << num << "] : " << result << endl;
	return result;
}
double integral_cos::value()
{
	double result = 0;
	double width = (max - min) / num;
	for (int i = 1; i <= num; i++)
		result += cos(min + i * width) * width;
	cout << name << "[" << min << "~" << max << "/n=" << num << "] : " << result << endl;
	return result;
}
double integral_exp::value()
{
	double result = 0;
	double width = (max - min) / num;
	for (int i = 1; i <= num; i++)
		result += exp(min + i * width) * width;
	cout << name << "[" << min << "~" << max << "/n=" << num << "] : " << result << endl;
	return result;
}
//输出运算符重载，输出提示词
istream& operator >>(istream& in, integral& _integral)
{
	while (1)
	{
		cout << "请输入" << _integral.name << "的下限、上限及区间划分数量" << endl;
		in >> _integral.min >> _integral.max >> _integral.num;
		if (in.good() && _integral.min <= _integral.max && _integral.num > 0)
			break;
		cout << "数据输入错误，请重新输入" << endl;
		in.clear();
		in.ignore(65536, '\n');
	}
	return in;
}
/* -- 替换标记行 -- 本行不要做任何改动 -- 本行不要删除 -- 在本行的下面不要加入任何自己的语句，作业提交后从本行开始会被替换 -- 替换标记行 -- */

/***************************************************************************
  函数名称：
  功    能：
  输入参数：
  返 回 值：
  说    明：fun_integral不准动，思考一下，integral应如何定义
***************************************************************************/
void fun_integral(integral& fRef)
{
	cin >> fRef;	//输入上下限、划分数
	cout << fRef.value() << endl;
	return;
}

/***************************************************************************
  函数名称：
  功    能：
  输入参数：
  返 回 值：
  说    明：main函数不准动
***************************************************************************/
int main()
{
	integral_sin s1;
	integral_cos s2;
	integral_exp s3;

	fun_integral(s1); //计算sinxdx的值
	fun_integral(s2); //计算cosxdx的值
	fun_integral(s3); //计算expxdx的值

	return 0;
}

//注：矩形计算取右值，输出为正常double格式