/* 2352018 信06 刘彦 */
#include <iostream>
#include <cmath>
using namespace std;

extern double a, b, c;
void fun1() 
{
	cout << "不是一元二次方程" << endl;
}
void fun2() 
{
	double x1, x2, x, delta;
	delta = b * b - 4 * a * c;
	x1 = (-b + sqrt(delta)) / (2 * a);
	x2 = (-b - sqrt(delta)) / (2 * a);
	if (fabs(x1) < 1e-6)
		x1 = 0;
	if (fabs(x2) < 1e-6)
		x2 = 0;
	cout << "有两个不等实根：" << endl;
	if (x2 > x1)
	{
		x = x1;
		x1 = x2;
		x2 = x;
	}
	cout << "x1=" << x1 << endl;
	cout << "x2=" << x2 << endl;
}
void fun3() 
{
	double x;
	x = (-b) / (2 * a);
	if (fabs(x) < 1e-6)
		x = 0;
	cout << "有两个相等实根：" << endl;
	cout << "x1=x2=" << x << endl;
}
void fun4() 
{
	double x1, x2;
	x1 = (-b) / (2 * a);
	x2 = (sqrt(-b * b + 4 * a * c)) / (2 * a);
	if (fabs(x1) < 1e-6)
		x1 = 0;
	if (fabs(x2) < 1e-6)
		x2 = 0;
	cout << "有两个虚根：" << endl;
	if (fabs(x1) >= 1e-6)
	{
		cout << "x1=" << x1 << "+" << fabs(x2) << "i" << endl;
		cout << "x2=" << x1 << "-" << fabs(x2) << "i" << endl;
	}
	else
	{
		if (fabs(x2) == 1)
		{
			cout << "x1=" << "i" << endl;
			cout << "x2=" << "-i" << endl;
		}
		else
		{
			cout << "x1=" << fabs(x2) << "i" << endl;
			cout << "x2=" << -fabs(x2) << "i" << endl;
		}
	}
}