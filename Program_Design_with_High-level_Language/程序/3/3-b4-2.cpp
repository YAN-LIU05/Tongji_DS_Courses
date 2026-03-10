/* 2352018 信06 刘彦 */
#include<iostream>
#include <iomanip>
#include<math.h>
using namespace std;
#define pi 3.14159

int main()
{
	int a, b, t;
	float S;
	cout << "请输入三角形的两边及其夹角(角度)" << endl;
	cin >> a >> b >> t;
	
	S = (a * b * sin(t * float(pi) / 180)) / 2;
	cout << setiosflags(ios::fixed) << setprecision(3);
	cout << "三角形面积为" << " : " << S << endl;

	return 0;
}