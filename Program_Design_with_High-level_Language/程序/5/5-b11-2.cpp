/* 2352018 信06 刘彦 */
#include <iostream>
#include <string>
//可按需增加需要的头文件
using namespace std;

const char chnstr[] = "零壹贰叁肆伍陆柒捌玖"; /* 所有输出大写 "零" ~ "玖" 的地方，只允许从这个数组中取值 */
string result;  /* 除result外，不再允许定义任何形式的全局变量 */

/* --允许添加需要的函数 --*/
/***************************************************************************
  函数名称：daxie
  功    能：转大写
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
void daxie(int num, int flag_of_zero)
{
    char arr[] = " ";
    if (num == 0 && flag_of_zero)
    {
        result = result + chnstr[0] + chnstr[1];
    }
    if (num > 0 && num < 10)
    {
        result = result + chnstr[2 * num] + chnstr[2 * num + 1];
    }
}
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
    int flag1, flag2, flag3, flag4, flag5, flag6, flag7;   //判断零的输出
    bool f, g, h, m, n, p, q, u, v, w;   //判断flag

    cout << "请输入[0-100亿)之间的数字:" << endl;
    cin >> x;

    x += 0.00001;
    shiyi = (int)(x / 1000000000);
    yi = (int)(x / 100000000 - shiyi * 10);
    qianwan = (int)(x / 10000000 - shiyi * 100 - yi * 10);
    baiwan = (int)(x / 1000000 - shiyi * 1000 - yi * 100 - qianwan * 10);
    shiwan = (int)(x / 100000 - shiyi * 10000 - yi * 1000 - qianwan * 100 - baiwan * 10);
    wan = (int)(x / 10000 - shiyi * 100000 - yi * 10000 - qianwan * 1000 - baiwan * 100 - shiwan * 10);
    qian = (int)(x / 1000 - shiyi * 1000000 - yi * 100000 - qianwan * 10000 - baiwan * 1000 - shiwan * 100 - wan * 10);
    bai = (int)(x / 100 - shiyi * 10000000 - yi * 1000000 - qianwan * 100000 - baiwan * 10000 - shiwan * 1000 - wan * 100 - qian * 10);
    shi = (int)(x / 10 - shiyi * 100000000 - yi * 10000000 - qianwan * 1000000 - baiwan * 100000 - shiwan * 10000 - wan * 1000 - qian * 100 - bai * 10);
    yuan = (int)((x / 10.0 - floor(x / 10)) * 10);
    y = floor(x);
    jiao = (int)((x - y) * 10);
    fen = (int)((x - y) * 100 - 10 * jiao);

    cout << "大写结果是:" << endl;

    daxie(shiyi, 0);
    if (shiyi)
    {
        result += "拾";
    }

    daxie(yi, 0);
    if (shiyi || yi)
    {
        result += "亿";
    }

    f = (!shiyi && !yi) || (!baiwan);
    if (f)
    {
        flag1 = 0;
    }
    else
    {
        flag1 = 1;
    }
    daxie(qianwan, flag1);
    if (qianwan)
    {
        result += "仟";
    }
    g = (!shiyi && !yi && !qianwan) || (!shiwan);
    if (g)
    {
        flag2 = 0;
    }
    else
    {
        flag2 = 1;
    }
    daxie(baiwan, flag2);
    if (baiwan)
    {
        result += "佰";
    }
    h = !shiyi && !yi && !qianwan && !baiwan;
    if (h)
    {
        flag3 = 0;
    }
    else if (wan)
    {
        flag3 = 1;
    }
    else
    {
        flag3 = 0;
    }
    daxie(shiwan, flag3);
    if (shiwan)
    {
        result += "拾";
    }
    daxie(wan, 0);
    m = qianwan || baiwan || shiwan || wan;
    if (m)
    {
        result += "万";
    }
    n = (!shiyi && !yi && !qianwan && !baiwan && !shiwan && !wan) || !bai;
    if (n)
    {
        flag4 = 0;
    }
    else
    {
        flag4 = 1;
    }
    daxie(qian, flag4);
    if (qian)
    {
        result += "仟";
    }

    u = (!shiyi && !yi && !qianwan && !baiwan && !shiwan && !wan && !qian) || !shi;
    if (u)
    {
        flag5 = 0;
    }
    else
    {
        flag5 = 1;
    }
    daxie(bai, flag5);
    if (bai)
    {
        result += "佰";
    }

    v = shiyi || yi || qianwan || baiwan || shiwan || wan || qian || bai;
    switch (v)
    {
        case 0:
            flag6 = 0;
            break;
        case 1:
            switch (yuan)
            {
                case 1:
                    flag6 = 1;
                    break;
                default:
                    flag6 = 0;
                    break;
            }
    }
    daxie(shi, flag6);
    if (shi)
    {
        result += "拾";
    }

    p = shiyi || yi || qianwan || baiwan || shiwan || wan || qian || bai || shi || jiao || fen;
    q = shiyi || yi || qianwan || baiwan || shiwan || wan || qian || bai || shi;
    if (p == 0)
    {
        daxie(yuan, 1);
        result += "圆";
    }
    else if (q || yuan)
    {
        daxie(yuan, 0);
        result += "圆";
    }

    w = !shiyi && !yi && !qianwan && !baiwan && !shiwan && !wan && !qian && !bai && !shi && !yuan;
    switch (w)
    {
        case 1:
            flag7 = 0;
            break;
        case 0:
            switch (fen)
            {
                case 0:
                    flag7 = 0;
                    break;
                default:
                    flag7 = 1;
            }
    }
    daxie(jiao, flag7);
    if (jiao)
    {
        result += "角";
    }
    daxie(fen, 0);
    if (fen)
    {
        result += "分";
    }
    else
    {
        result += "整";
    }


    cout << result << endl;  /* 转换得到的大写结果，只允许用本语句输出，其它地方不允许以任何形式对大写结果进行全部/部分输出 */
    return 0;
}