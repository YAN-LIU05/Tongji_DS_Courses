/* 2352018 信06 刘彦 */
#include <iostream>  
using namespace std;

int main() 
{
    double s;
    int a, b, c, d, e, p, q, x, y, z, sum, t;
  
    cout << "请输入找零值：" << endl;
    cin >> s;

    if (s >= 0.01 && s < 100) {
        sum = static_cast<int>(s * 100);

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
        cout << "共" << t << "张找零，具体如下：" << endl;

        switch (a) {
            case 0:
                break;
            default:
                cout << "50元 : " << a << "张" << endl;
                break;
        }
        switch (b) {
            case 0:
                break;
            default:
                cout << "20元 : " << b << "张" << endl;
                break;
        }
        switch (c) {
            case 0:
                break;
            default:
                cout << "10元 : " << c << "张" << endl;
                break;
        }
        switch (d) {
            case 0:
                break;
            default:
                cout << "5元  : " << d << "张" << endl;
                break;
        }
        switch (e) {
            case 0:
                break;
            default:
                cout << "1元  : " << e << "张" << endl;
                break;
        }
        switch (p) {
            case 0:
                break;
            default:
                cout << "5角  : " << p << "张" << endl;
                break;
        }
        switch (q) {
            case 0:
                break;
            default:
                cout << "1角  : " << q << "张" << endl;
                break;
        }
        switch (x) {
            case 0:
                break;
            default:
                cout << "5分  : " << x << "张" << endl;
                break;
        }
        switch (y) {
            case 0:
                break;
            default:
                cout << "2分  : " << y << "张" << endl;
                break;
        }
        switch (z) {
            case 0:
                break;
            default:
                cout << "1分  : " << z << "张" << endl;
                break;
        }
    }
    else {
        cout << "输入错误，请重新输入" << endl;
    }

    return 0;
}