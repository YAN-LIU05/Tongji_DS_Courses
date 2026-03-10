/* 2352018 信06 刘彦 */
#include <iostream>
using namespace std;

/* 可根据需要添加相应的内容 */

/***************************************************************************
  函数名称：
  功    能：输出大写的0~9
  输入参数：
  返 回 值：
  说    明：除本函数外，不允许任何函数中输出“零”-“玖”!!!!!!
***************************************************************************/
void daxie(int num, int flag_of_zero)
{
	/* 不允许对本函数做任何修改 */
	switch (num) {
		case 0:
			if (flag_of_zero)	//此标记什么意思请自行思考
				cout << "零";
			break;
		case 1:
			cout << "壹";
			break;
		case 2:
			cout << "贰";
			break;
		case 3:
			cout << "叁";
			break;
		case 4:
			cout << "肆";
			break;
		case 5:
			cout << "伍";
			break;
		case 6:
			cout << "陆";
			break;
		case 7:
			cout << "柒";
			break;
		case 8:
			cout << "捌";
			break;
		case 9:
			cout << "玖";
			break;
		default:
			cout << "error";
			break;
	}
}

/* 可根据需要自定义其它函数(也可以不定义) */

/***************************************************************************
  函数名称：
  功    能：
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
int main()
{
	int yuan, shi, bai, qian, wan, shiwan, baiwan, qianwan, yi, shiyi, jiao, fen;
	double x, y;
	cout << "请输入[0-100亿)之间的数字:" << endl;
	cin >> x;

	x += 0.00001;
	shiyi = int(x / 1000000000);
	yi = int(x / 100000000 - shiyi * 10);
	qianwan = int(x / 10000000 - shiyi * 100 - yi * 10);
	baiwan = int(x / 1000000 - shiyi * 1000 - yi * 100 - qianwan * 10);
	shiwan = int(x / 100000 - shiyi * 10000 - yi * 1000 - qianwan * 100 - baiwan * 10);
	wan = int(x / 10000 - shiyi * 100000 - yi * 10000 - qianwan * 1000 - baiwan * 100 - shiwan * 10);
	qian = int(x / 1000 - shiyi * 1000000 - yi * 100000 - qianwan * 10000 - baiwan * 1000 - shiwan * 100 - wan * 10);
	bai = int(x / 100 - shiyi * 10000000 - yi * 1000000 - qianwan * 100000 - baiwan * 10000 - shiwan * 1000 - wan * 100 - qian * 10);
	shi = int(x / 10 - shiyi * 100000000 - yi * 10000000 - qianwan * 1000000 - baiwan * 100000 - shiwan * 10000 - wan * 1000 - qian * 100 - bai * 10);
	yuan = int((x / 10.0 - floor(x / 10)) * 10);
	y = floor(x);
	jiao = int((x - y) * 10);
	fen = int((x - y) * 100 - 10 * jiao);

	int flag1, flag2, flag3, flag4, flag5, flag6, flag7;
	cout << "大写结果是:" << endl;
	daxie(shiyi, 0);
	if (shiyi) {
		cout << "拾";
	}

	daxie(yi, 0);
	if (shiyi || yi) {
		cout << "亿";
	}

	if ((!shiyi && !yi) || (!baiwan)) {
		flag1 = 0;
	}
	else {
		flag1 = 1;
	}
	daxie(qianwan, flag1);
	if (qianwan) {
		cout << "仟";
	}

	if ((!shiyi && !yi && !qianwan) || (!shiwan)) {
		flag2 = 0;
	}
	else {
		flag2 = 1;
	}
	daxie(baiwan, flag2);
	if (baiwan) {
		cout << "佰";
	}

	if (!shiyi && !yi && !qianwan && !baiwan) {
		flag3 = 0;
	}
	else if (wan) {
		flag3 = 1;
	}
	else {
		flag3 = 0;
	}
	daxie(shiwan, flag3);
	if (shiwan) {
		cout << "拾";
		}

	daxie(wan, 0);
	if (qianwan || baiwan || shiwan || wan) {
		cout << "万";
	}

	if ((!shiyi && !yi && !qianwan && !baiwan && !shiwan && !wan) || !bai) {
		flag4 = 0;
	}
	else {
		flag4 = 1;
	}
	daxie(qian, flag4);
	if (qian) {
		cout << "仟";
	}

	if ((!shiyi && !yi && !qianwan && !baiwan && !shiwan && !wan && !qian) || !shi) {
		flag5 = 0;
	}
	else {
		flag5 = 1;
	}
	daxie(bai, flag5);
	if (bai) {
		cout << "佰";
	}

	bool u, v;
	u = shiyi || yi || qianwan || baiwan || shiwan || wan || qian || bai;
	v = yuan;
	switch (u) {
		case 0:
			flag6 = 0;
			break;
		case 1:
			switch (v) {
				case 1:
					flag6 = 1;
					break;
				default:
					flag6 = 0;
					break;
			}
	}
	daxie(shi, flag6);
	if (shi) {
		cout << "拾";
	}

	bool p, q;
	p = shiyi || yi || qianwan || baiwan || shiwan || wan || qian || bai || shi || jiao || fen;
	q = shiyi || yi || qianwan || baiwan || shiwan || wan || qian || bai || shi;
	if (p == 0) {
		daxie(yuan, 1);
		cout << "圆";
	}
	else if (q || yuan) {
		daxie(yuan, 0);
		cout << "圆";
	}

	bool w;
	w = !shiyi && !yi && !qianwan && !baiwan && !shiwan && !wan && !qian && !bai && !shi && !yuan;
	switch (w) {
		case 1:
			flag7 = 0;
			break;
		case 0:
			switch (fen) {
				case 0:
					flag7 = 0;
					break;
				default:
					flag7 = 1;
			}
	}
	daxie(jiao, flag7);
	if (jiao) {
		cout << "角";
		}

	daxie(fen, 0);
	if (fen) {
		cout << "分";
	}
	else {
		cout << "整";
	}

	cout << endl;
	return 0;
}