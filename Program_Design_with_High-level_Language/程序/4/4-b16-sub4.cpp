/* 2352018 信06 刘彦 */
#include <iostream>
#include <cmath>
using namespace std;

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