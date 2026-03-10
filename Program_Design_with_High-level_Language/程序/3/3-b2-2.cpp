/* 2352018 信06 刘彦 */
#include <iostream>
using namespace std;

int main()
{
	int a, a1, a2, a3, a4, a5;
	cout << "请输入一个[1..30000]间的整数:" << endl;
	cin >> a;
	
	a5 = a % 10;
	a4 = (a / 10) % 10;
	a3 = (a / 100) % 10;
	a2 = (a / 1000) % 10;
	a1 = a / 10000;

	cout << "万位" << " : " << a1 << endl;
	cout << "千位" << " : " << a2 << endl;
	cout << "百位" << " : " << a3 << endl;
	cout << "十位" << " : " << a4 << endl;
	cout << "个位" << " : " << a5 << endl;
	
	return 0;
}