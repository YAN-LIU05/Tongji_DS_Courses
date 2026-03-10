/* 2352018 信06 刘彦 */
#include <iostream>
#include <cmath>
using namespace std;

double a, b, c;
void fun1(void);
void fun2(void);
void fun3(void);
void fun4(void);

int main()
{
	int flag = 0;
	double delta;
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
		fun3();
	else if (flag == 2)
		fun2();
	else
		fun4();

	return 0;
}