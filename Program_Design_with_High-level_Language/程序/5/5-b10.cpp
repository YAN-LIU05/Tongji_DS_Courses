/* 2352018 信06 刘彦 */
#include <iostream>
#include <iomanip>
#include <conio.h>
using namespace std;

int zeller(int y, int m,int d)
{
	int m1, c, y1, w;
	if (m < 3) {
		c = (y - 1) / 100;
		y1 = y - 1 - c * 100;
		m1 = 12 + m;
	}
	else {
		c = y / 100;
		y1 = y - c * 100;
		m1 = m;
	}
	w = y1 + (y1 / 4) + (c / 4) - 2 * c + (13 * (m1 + 1) / 5) + d - 1;
	while (w < 0) {
		w += 7;
	}
	if (w % 7 == 0) {
		w = 7;
	}
	else
		w = w % 7;
	return w;
}
int runnian(int a) {
	if ((a % 4 != 0) || (a % 100 == 0) && (a % 400 != 0)) {
		return 0;
	}
	else
		return 1;
}
int main() {
	int a,nian,i,j;
	while (1) {
		cout << "请输入年份[1900-2100]" << endl;
		cin >> a;
		if (cin.good() == 1 && a >= 1900 && a <= 2100) {
			break;
		}
		else if (cin.good() == 1) {
			continue;
		}
		else {
			cin.clear();
			while (getchar() != '\n');
		}
	}
	nian = runnian(a);
	int yuefen[12] ;
	if (nian == 0) {
		for (i = 0; i < 12; i++) {
			if ((i + 1) == 1 || (i + 1) == 3 || (i + 1) == 5 || (i + 1) == 7 || (i + 1) == 8 || (i + 1) == 10 || (i + 1) == 12) {
				yuefen[i] = 31;
			}
			else if ((i + 1) == 4 || (i + 1) == 6 || (i + 1) == 9 || (i + 1) == 11) {
				yuefen[i] = 30;
			}
			else {
				yuefen[i] = 28;
			}
		}
	}
	else {
		for (i = 0; i < 12; i++) {
			if ((i + 1) == 1 || (i + 1) == 3 || (i + 1) == 5 || (i + 1) == 7 || (i + 1) == 8 || (i + 1) == 10 || (i + 1) == 12) {
				yuefen[i] = 31;
			}
			else if ((i + 1) == 4 || (i + 1) == 6 || (i + 1) == 9 || (i + 1) == 11) {
				yuefen[i] = 30;
			}
			else {
				yuefen[i] = 29;
			}
		}
	}
	int xingqi[12][31] = {0};
	for (i = 0; i < 12; i++) {
		for (j = 0; j < yuefen[i]; j++) {
			xingqi[i][j] = zeller(a, i + 1, j + 1);
		}
	}


	cout << a << "年的日历:" << endl;
	cout << endl;

	cout <<   "            1月                             2月                             3月" << endl;
	cout << "Sun Mon Tue Wed Thu Fri Sat";
	cout << "     Sun Mon Tue Wed Thu Fri Sat";
	cout << "     Sun Mon Tue Wed Thu Fri Sat" << endl;
	
	int k[12];
	int m;

	for (m = 0; m < 3; m++) {
		j = xingqi[m][0];
		if (j != 7) {
			cout << setw(j * 4) << " ";
		}
		else {
			j = 0;
		}
		for (i = 0; i < 7 - j; i++) {
			if ((i + 1) <= yuefen[m]) {
				cout << setiosflags(ios::left) << setw(4) << (i + 1);
			}
			else {
				cout << setw(4) << " ";
			}
		}
		k[m] = i;
		cout << "    ";
	}
	cout << endl;

	while (k[0] < 31 || k[1] < 28 || k[2] < 31) {
		for (m = 0; m < 3; m++) {
			if (k[m] > (yuefen[m] - 1)) {
				j = 7;
			}
			else {
				j = xingqi[m][k[m]];
			}
			if (j != 7) {
				cout << setw(j * 4) << " ";
			}
			for (i = k[m]; i < k[m] + 7; i++) {
				if ((i + 1) <= yuefen[m]) {
					cout << setiosflags(ios::left) << setw(4) << (i + 1);
				}
				else {
					cout << setw(4) << " ";
				}
			}
			k[m] = i;
			cout << "    ";
		}
		cout << endl;
	}

	cout << endl;

	cout << "            4月                             5月                             6月" << endl;
	cout << "Sun Mon Tue Wed Thu Fri Sat";
	cout << "     Sun Mon Tue Wed Thu Fri Sat";
	cout << "     Sun Mon Tue Wed Thu Fri Sat" << endl;
	for (m = 3; m < 6; m++) {
		j = xingqi[m][0];
		if (j != 7) {
			cout << setw(j * 4) << " ";
		}
		else {
			j = 0;
		}
		for (i = 0; i < 7 - j; i++) {
			if ((i + 1) <= yuefen[m]) {
				cout << setiosflags(ios::left) << setw(4) << (i + 1);
			}
			else {
				cout << setw(4) << " ";
			}
		}
		k[m] = i;
		cout << "    ";
	}
	cout << endl;

	while (k[3] < 30 || k[4] < 31 || k[5] < 30) {
		for (m = 3; m < 6; m++) {
			if (k[m] > (yuefen[m] - 1)) {
				j = 7;
			}
			else {
				j = xingqi[m][k[m]];
			}
			if (j != 7) {
				cout << setw(j * 4) << " ";
			}
			for (i = k[m]; i < k[m] + 7; i++) {
				if ((i + 1) <= yuefen[m]) {
					cout << setiosflags(ios::left) << setw(4) << (i + 1);
				}
				else {
					cout << setw(4) << " ";
				}
			}
			k[m] = i;
			cout << "    ";
		}
		cout << endl;
	}


	cout << endl;

	cout << "            7月                             8月                             9月" << endl;
	cout << "Sun Mon Tue Wed Thu Fri Sat";
	cout << "     Sun Mon Tue Wed Thu Fri Sat";
	cout << "     Sun Mon Tue Wed Thu Fri Sat" << endl;


	for (m = 6; m < 9; m++) {
		j = xingqi[m][0];
		if (j != 7) {
			cout << setw(j * 4) << " ";
		}
		else {
			j = 0;
		}
		for (i = 0; i < 7 - j; i++) {
			if ((i + 1) <= yuefen[m]) {
				cout << setiosflags(ios::left) << setw(4) << (i + 1);
			}
			else {
				cout << setw(4) << " ";
			}
		}
		k[m] = i;
		cout << "    ";
	}
	cout << endl;

	while (k[6] < 31 || k[7] < 31 || k[8] < 30) {
		for (m = 6; m < 9; m++) {
			if (k[m] > (yuefen[m]-1)) {
				j = 7;
			}
			else {
				j = xingqi[m][k[m]];
			}
			if (j != 7) {
				cout << setw(j * 4) << " ";
			}
			for (i = k[m]; i < k[m] + 7; i++) {
				if ((i + 1) <= yuefen[m]) {
					cout << setiosflags(ios::left) << setw(4) << (i + 1);
				}
				else {
					cout << setw(4) << " ";
				}
			}
			k[m] = i;
			cout << "    ";
		}
		cout << endl;
	}
	cout << endl;

	cout <<  "           10月                            11月                            12月" << endl;
	cout << "Sun Mon Tue Wed Thu Fri Sat";
	cout << "     Sun Mon Tue Wed Thu Fri Sat";
	cout << "     Sun Mon Tue Wed Thu Fri Sat" << endl;
	for (m = 9; m < 12; m++) {
		j = xingqi[m][0];
		if (j != 7) {
			cout << setw(j * 4) << " ";
		}
		else {
			j = 0;
		}
		for (i = 0; i < 7 - j; i++) {
			if ((i + 1) <= yuefen[m]) {
				cout << setiosflags(ios::left) << setw(4) << (i + 1);
			}
			else {
				cout << setw(4) << " ";
			}
		}
		k[m] = i;
		cout << "    ";
	}
	cout << endl;

	while (k[9] < 31 || k[10]<30 || k[11] < 31) {
		for (m = 9; m < 12; m++) {
			if (k[m] > (yuefen[m] - 1)) {
				j = 7;
			}
			else {
				j = xingqi[m][k[m]];
			}
			if (j != 7) {
				cout << setw(j * 4) << " ";
			}
			for (i = k[m]; i < k[m] + 7; i++) {
				if ((i + 1) <= yuefen[m]) {
					cout << setiosflags(ios::left) << setw(4) << (i + 1);
				}
				else {
					cout << setw(4) << " ";
				}
			}
			k[m] = i;
			cout << "    ";
		}
		cout << endl;
	}
	cout << endl;
	cout << endl;
	return 0;
}
