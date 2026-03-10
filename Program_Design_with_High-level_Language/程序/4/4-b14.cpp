/* 2352018 信06 刘彦 */
#include <iostream>
#include <cmath>
using namespace std;

void fun1()
{
	cout << "不是一元二次方程" << endl;
}
void fun2(double a, double b, double c)
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
void fun3(double a, double b, double c)
{
	double x;
	x = (-b) / (2 * a);
	if (fabs(x) < 1e-6)
		x = 0;
	cout << "有两个相等实根：" << endl;
	cout << "x1=x2=" << x << endl;
}
void fun4(double a, double b, double c)
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


int main()
{
	int flag = 0;
	double a, b, c, delta;
	cout << "请输入一元二次方程的三个系数a,b,c:" << endl;
	cin >> a >> b >> c;
	if (fabs(a) < 1e-6)
		a = 0;
	if (fabs(b) < 1e-6)
		b = 0;
	if (fabs(c) < 1e-6)
		c = 0;
	delta = b * b - 4 * a * c;
	if (fabs(delta) < 1e-6)
		flag = 1;
	else if ((delta) >= 1e-6)
		flag = 2;
	if (a == 0)
		fun1();
	else if (flag == 1)
		fun3(a, b, c);
	else if (flag == 2)
		fun2(a, b, c);
	else
		fun4(a, b, c);

	return 0;
}