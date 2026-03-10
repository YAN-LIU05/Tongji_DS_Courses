/* 2352018 信06 刘彦 */
#include<iostream>
#include <iomanip>
using namespace std;

int main()
{
	double r, h, C, S1, S2, V1, V2;
	const double pi = 3.14159;
	cout << "请输入半径和高度" << endl;
    cin >> r >> h;

	C = pi * r * 2;
	S1 = pi * r * r;
	S2 = pi * 4 * r * r;
	V1 = (4 * pi * r * r * r) / 3;
	V2 = pi * r * r * h;

	cout << setiosflags(ios::fixed) << setprecision(2);
	cout << setiosflags(ios::left);
	cout << setw(10) << "圆周长" << " : " << C << endl;
	cout << setw(10) << "圆面积" << " : " << S1 << endl;
	cout << setw(10) << "圆球表面积" << " : " << S2 << endl;
	cout << setw(10) << "圆球体积  " << " ; " << V1 << endl;
	cout << setw(10) << "圆柱体积  " << " : " << V2 << endl;

	return 0;
}