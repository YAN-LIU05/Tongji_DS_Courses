/* 2352018 ĞÅ06 ÁõÑå */
#include <iostream>
#include <cmath>
using namespace std;

int main()
{
	int a, b, c, d, e, f, g, h, i, j, m, n;
	double x, y;
	cout << "ÇëÊäÈë[0-100ÒÚ)Ö®¼äµÄÊı×Ö:" << endl;
	cin >> x;

	x += 0.00001;
	j = int(x / 1000000000);
	i = int(x / 100000000 - j * 10);
	h = int(x / 10000000 - j * 100 - i * 10);
	g = int(x / 1000000 - j * 1000 - i * 100 - h * 10);
	f = int(x / 100000 - j * 10000 - i * 1000 - h * 100 - g * 10);
	e = int(x / 10000 - j * 100000 - i * 10000 - h * 1000 - g * 100 - f * 10);
	d = int(x / 1000 - j * 1000000 - i * 100000 - h * 10000 - g * 1000 - f * 100 - e * 10);
	c = int(x / 100 - j * 10000000 - i * 1000000 - h * 100000 - g * 10000 - f * 1000 - e * 100 - d * 10);
	b = int(x / 10 - j * 100000000 - i * 10000000 - h * 1000000 - g * 100000 - f * 10000 - e * 1000 - d * 100 - c * 10);
	a = int((x / 10.0 - floor(x / 10)) * 10);
	y = floor(x);
	m = int((x - y) * 10);
	n = int((x - y) * 100 - 10 * m);

	cout << "´óĞ´½á¹ûÊÇ:" << endl;

	switch (j) {
		case 1:
			cout << "Ò¼Ê°";
			break;
		case 2:
			cout << "·¡Ê°";
			break;
		case 3:
			cout << "ÈşÊ°";
			break;
		case 4:
			cout << "ËÁÊ°";
			break;
		case 5:
			cout << "ÎéÊ°";
			break;
		case 6:
			cout << "Â½Ê°";
			break;
		case 7:
			cout << "ÆâÊ°";
			break;
		case 8:
			cout << "°ÆÊ°";
			break;
		case 9:
			cout << "¾ÁÊ°";
			break;
		case 0:
			cout << "";
			break;
	}

	switch (i) {
		case 1:
			cout << "Ò¼ÒÚ";
			break;
		case 2:
			cout << "·¡ÒÚ";
			break;
		case 3:
			cout << "ÈşÒÚ";
			break;
		case 4:
			cout << "ËÁÒÚ";
			break;
		case 5:
			cout << "ÎéÒÚ";
			break;
		case 6:
			cout << "Â½ÒÚ";
			break;
		case 7:
			cout << "ÆâÒÚ";
			break;
		case 8:
			cout << "°ÆÒÚ";
			break;
		case 9:
			cout << "¾ÁÒÚ";
			break;
		case 0:
			if (j == 0) {
				cout << "";
			}
			else {
				cout << "ÒÚ";
			}
			break;
	}

	switch (h) {
		case 1:
			cout << "Ò¼Çª";
			break;
		case 2:
			cout << "·¡Çª";
			break;
		case 3:
			cout << "ÈşÇª";
			break;
		case 4:
			cout << "ËÁÇª";
			break;
		case 5:
			cout << "ÎéÇª";
			break;
		case 6:
			cout << "Â½Çª";
			break;
		case 7:
			cout << "ÆâÇª";
			break;
		case 8:
			cout << "°ÆÇª";
			break;
		case 9:
			cout << "¾ÁÇª";
			break;
		case 0:
			if ((!i && !j) || (!g)) {
				cout << "";
			}
			else {
				cout << "Áã";
			}
	}

	switch (g) {
		case 1:
			cout << "Ò¼°Û";
			break;
		case 2:
			cout << "·¡°Û";
			break;
		case 3:
			cout << "Èş°Û";
			break;
		case 4:
			cout << "ËÁ°Û";
			break;
		case 5:
			cout << "Îé°Û";
			break;
		case 6:
			cout << "Â½°Û";
			break;
		case 7:
			cout << "Æâ°Û";
			break;
		case 8:
			cout << "°Æ°Û";
			break;
		case 9:
			cout << "¾Á°Û";
			break;
		case 0:
			if ((!h && !i && !j) || !f) {
				cout << "";
			}
			else {
				cout << "Áã";
			}
			break;
	}

	switch (f) {
		case 1:
			cout << "Ò¼Ê°";
			break;
		case 2:
			cout << "·¡Ê°";
			break;
		case 3:
			cout << "ÈşÊ°";
			break;
		case 4:
			cout << "ËÁÊ°";
			break;
		case 5:
			cout << "ÎéÊ°";
			break;
		case 6:
			cout << "Â½Ê°";
			break;
		case 7:
			cout << "ÆâÊ°";
			break;
		case 8:
			cout << "°ÆÊ°";
			break;
		case 9:
			cout << "¾ÁÊ°";
			break;
		case 0:
			if (!g && !h && !i && !j) {
				cout << "";
			}
			else if (e) {
				cout << "Áã";
			}
			break;
	}

	switch (e) {
		case 1:
			cout << "Ò¼Íò";
			break;
		case 2:
			cout << "·¡Íò";
			break;
		case 3:
			cout << "ÈşÍò";
			break;
		case 4:
			cout << "ËÁÍò";
			break;
		case 5:
			cout << "ÎéÍò";
			break;
		case 6:
			cout << "Â½Íò";
			break;
		case 7:
			cout << "ÆâÍò";
			break;
		case 8:
			cout << "°ÆÍò";
			break;
		case 9:
			cout << "¾ÁÍò";
			break;
		case 0:
			if (f || g || h) {
				cout << "Íò";
			}
			break;
	}

	switch (d) {
		case 1:
			cout << "Ò¼Çª";
			break;
		case 2:
			cout << "·¡Çª";
			break;
		case 3:
			cout << "ÈşÇª";
			break;
		case 4:
			cout << "ËÁÇª";
			break;
		case 5:
			cout << "ÎéÇª";
			break;
		case 6:
			cout << "Â½Çª";
			break;
		case 7:
			cout << "ÆâÇª";
			break;
		case 8:
			cout << "°ÆÇª";
			break;
		case 9:
			cout << "¾ÁÇª";
			break;
		case 0:
			if ((!e && !f && !g && !h && !i && !j) || !c) {
				cout << "";
			}
			else {
				cout << "Áã";
			}
			break;
	}

	switch (c) {
		case 1:
			cout << "Ò¼°Û";
			break;
		case 2:
			cout << "·¡°Û";
			break;
		case 3:
			cout << "Èş°Û";
			break;
		case 4:
			cout << "ËÁ°Û";
			break;
		case 5:
			cout << "Îé°Û";
			break;
		case 6:
			cout << "Â½°Û";
			break;
		case 7:
			cout << "Æâ°Û";
			break;
		case 8:
			cout << "°Æ°Û";
			break;
		case 9:
			cout << "¾Á°Û";
			break;
		case 0:
			if ((!d && !e && !f && !g && !h && !i && !j) || !b) {
				cout << "";
			}
			else {
				cout << "Áã";
			}
			break;
	}

	bool u, v;
	u = c || d || e || f || g || h || i || j;
	v = a;
	switch (b) {
		case 1:
			cout << "Ò¼Ê°";
			break;
		case 2:
			cout << "·¡Ê°";
			break;
		case 3:
			cout << "ÈşÊ°";
			break;
		case 4:
			cout << "ËÁÊ°";
			break;
		case 5:
			cout << "ÎéÊ°";
			break;
		case 6:
			cout << "Â½Ê°";
			break;
		case 7:
			cout << "ÆâÊ°";
			break;
		case 8:
			cout << "°ÆÊ°";
			break;
		case 9:
			cout << "¾ÁÊ°";
			break;
		case 0:
			switch (u) {
				case 0:
					cout << "";
					break;
				case 1:
					switch (v) {
						case 1:
							cout << "Áã";
							break;
						default:
							cout << "";
							break;
					}
			}
	}

	bool p, q;
	p = b || c || d || e || f || g || h || i || j || m || n;
	q = b || c || d || e || f || g || h || i || j;
	switch (a) {
		case 1:
			cout << "Ò¼Ô²";
			break;
		case 2:
			cout << "·¡Ô²";
			break;
		case 3:
			cout << "ÈşÔ²";
			break;
		case 4:
			cout << "ËÁÔ²";
			break;
		case 5:
			cout << "ÎéÔ²";
			break;
		case 6:
			cout << "Â½Ô²";
			break;
		case 7:
			cout << "ÆâÔ²";
			break;
		case 8:
			cout << "°ÆÔ²";
			break;
		case 9:
			cout << "¾ÁÔ²";
			break;
		case 0:
			switch (p) {
				case 0:
					cout << "ÁãÔ²";
					break;
				case 1:
					switch (q) {
						case 1:
							cout << "Ô²";
							break;
						default:
							cout << "";
							break;
					}
			}
			break;
	}

	bool w;
	w = !a && !b && !c && !d && !e && !f && !g && !h && !i && !j;
	switch (m) {
		case 1:
			cout << "Ò¼½Ç";
			break;
		case 2:
			cout << "·¡½Ç";
			break;
		case 3:
			cout << "Èş½Ç";
			break;
		case 4:
			cout << "ËÁ½Ç";
			break;
		case 5:
			cout << "Îé½Ç";
			break;
		case 6:
			cout << "Â½½Ç";
			break;
		case 7:
			cout << "Æâ½Ç";
			break;
		case 8:
			cout << "°Æ½Ç";
			break;
		case 9:
			cout << "¾Á½Ç";
			break;
		case 0:
			switch (w) {
				case 1:
					break;
				case 0:
					switch (n) {
						case 0:
							break;
						default:
							cout << "Áã";
					}
			}
	}

	switch (n) {
		case 1:
			cout << "Ò¼·Ö";
			break;
		case 2:
			cout << "·¡·Ö";
			break;
		case 3:
			cout << "Èş·Ö";
			break;
		case 4:
			cout << "ËÁ·Ö";
			break;
		case 5:
			cout << "Îé·Ö";
			break;
		case 6:
			cout << "Â½·Ö";
			break;
		case 7:
			cout << "Æâ·Ö";
			break;
		case 8:
			cout << "°Æ·Ö";
			break;
		case 9:
			cout << "¾Á·Ö";
			break;
		case 0:
			cout << "Õû";
			break;
	}

	cout << endl;

	return 0;
}