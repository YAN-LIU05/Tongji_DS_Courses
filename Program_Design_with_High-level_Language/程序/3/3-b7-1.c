/* 2352018 信06 刘彦 */
#define _CRT_SECURE_NO_WARNINGS
#include<stdio.h>

int main()
{
	double s;
	int a, b, c, d, e, p, q, x, y, z, sum, t;

    printf("请输入找零值：\n");
    scanf("%lf", &s);

    if (s >= 0.01 && s < 100) {
        sum = (int)(s * 100);

        a = sum / 5000; // 50元  
        b = (sum - 5000 * a) / 2000;// 20元  
        c = (sum - 5000 * a - 2000 * b) / 1000;// 10元  
        d = (sum - 5000 * a - 2000 * b - c * 1000) / 500;// 5元
        e = (sum - 5000 * a - 2000 * b - c * 1000 - 500 * d) / 100;// 1元
        p = ((sum - 5000 * a - 2000 * b - c * 1000 - 500 * d - e * 100) / 50);// 5角
        q = ((sum - 5000 * a - 2000 * b - c * 1000 - 500 * d - e * 100 - 50 * p) / 10);// 1角
        x = ((sum - 5000 * a - 2000 * b - c * 1000 - 500 * d - e * 100 - 50 * p - 10 * q) / 5);// 5分
        y = ((sum - 5000 * a - 2000 * b - c * 1000 - 500 * d - e * 100 - 50 * p - 10 * q - x * 5) / 2);// 2分
        z = sum - 5000 * a - 2000 * b - c * 1000 - 500 * d - e * 100 - 50 * p - 10 * q - 5 * x - 2 * y;// 1分

        t = a + b + c + d + e + p + q + x + y + z;
        printf("共%d张找零，具体如下：\n", t);

        switch (a) {
            case 0:
                break;
            default:
                printf("50元 : %d张\n", a);
                break;
        }
        switch (b) {
            case 0:
                break;
            default:
                printf("20元 : %d张\n", b);
                break;
        }
        switch (c) {
            case 0:
                break;
            default:
                printf("10元 : %d张\n", c);
                break;
        }
        switch (d) {
            case 0:
                break;
            default:
                printf("5元  : %d张\n", d);
                break;
        }
        switch (e) {
            case 0:
                break;
            default:
                printf("1元  : %d张\n", e);
                break;
        }
        switch (p) {
            case 0:
                break;
            default:
                printf("5角  : %d张\n", p);
                break;
        }
        switch (q) {
            case 0:
                break;
            default:
                printf("1角  : %d张\n", q);
                break;
        }
        switch (x) {
            case 0:
                break;
            default:
                printf("5分  : %d张\n", x);
                break;
        }
        switch (y) {
            case 0:
                break;
            default:
                printf("2分  : %d张\n", y);
                break;
        }
        switch (z) {
            case 0:
                break;
            default:
                printf("1分  : %d张\n", z);
                break;
        }
    }
    else {
        printf("输入错误，请重新输入");
    }

	return 0;
}