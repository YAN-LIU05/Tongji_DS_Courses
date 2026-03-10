/* 2352018 信06 刘彦 */
#include <iostream>
#include <cmath>
using namespace std;

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