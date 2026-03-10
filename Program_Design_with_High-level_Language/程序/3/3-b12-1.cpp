/* 2352018 信06 刘彦 */
#include <iostream>
using namespace std;

int main()
{
	int x;

	while (1) {
		cout << "请输入x的值[0-100] : ";
		cin >> x;   //读入x的方式必须是 cin>>int型变量，不允许其他方式

		if ((x >= 0 && x <= 100) && cin.good() == 1) {
			break;
		}
		else if (cin.good() == 0) {
			cin.clear();   //重置输入流的状态
			while (getchar() != '\n');   //使用getchar()函数持续读取字符，直到读取到换行符\n为止
		}
	}

	cout << "cin.good()=" << cin.good() << " x=" << x << endl; //此句不准动，并且要求输出时good为1

	return 0;
}