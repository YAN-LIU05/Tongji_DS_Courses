/* 2352018 信06 刘彦 */
#include <iostream>
#include <ctime>
#include <cstdlib>

using namespace std;

static const char other[] = "~!@#$%^&*()-_=+[],.?";

// 函数声明
int input(int code, int Capital, int Lower, int Digit, int Other);
void initialize(char password[], int length);
void fill(char password[], int code, int Capital, int Lower, int Digit, int Other);
void disrupt(char password[], int length);
void print(char password[], int length);

int main() 
{
    srand((unsigned int)(time(0)));

    int code, Capital, Lower, Digit, Other;
    cout << "请输入密码长度(12-16)， 大写字母个数(≥2)， 小写字母个数(≥2)， 数字个数(≥2)， 其它符号个数(≥2)" << endl;
    cin >> code >> Capital >> Lower >> Digit >> Other;
    if (cin.fail())
    {
        cout << "输入非法" << endl;
        return -1;
    }
    int in = input(code, Capital, Lower, Digit, Other);
    switch (in)
    {
        case 1:
            cout << "密码长度[" << code << "]不正确" << endl;
            break;
        case 2:
            cout << "大写字母个数[" << Capital << "]不正确" << endl;
            break;
        case 3:
            cout << "小写字母个数[" << Lower << "]不正确" << endl;
            break;
        case 4:
            cout << "数字个数[" << Digit << "]不正确" << endl;
            break;
        case 5:
            cout << "其它符号个数[" << Other << "]不正确" << endl;
            break;
        case 6:
            cout << "所有字符类型之和[" << Capital << "+" << Lower << "+" << Digit << "+" << Other << "]大于总密码长度[" << code << "]" << endl;
            break;
        default:
            cout << code << " " << Capital << " " << Lower << " " << Digit << " " << Other << endl;
            const int arraySize = 10; // 要生成的密码数量
            for (int i = 0; i < arraySize; ++i) {
                char password[17]; // +1 用于字符串结束符 '\0'
                initialize(password, code);
                fill(password, code, Capital, Lower, Digit, Other);
                disrupt(password, code);
                print(password, code);
                cout << endl; // 密码之间空一行
            }
    }

    return 0;
}

// 输入验证函数
int input(int code, int Capital, int Lower, int Digit, int Other)
{
    if (code < 12 || code > 16)
        return 1;
    if (Capital < 2 || Capital > code)
        return 2;
    else if (Lower < 2 || Lower > code)
        return 3;
    else if (Digit < 2 || Digit > code)
        return 4;
    else if (Other < 2 || Other > code)
        return 5;
    else if ((Capital + Lower + Digit + Other) > code)
        return 6;

    return 0;
}

// 初始化密码数组函数
void initialize(char password[], int length) 
{
    for (int i = 0; i < length; ++i) 
    {
        password[i] = 0; 
    }
    password[length] = '\0'; // 添加字符串结束符
}


// 主函数，生成密码
void fill(char password[], int length, int Capital, int Lower, int Digit, int Other)
{
    // 首先生成满足最小要求的密码字符
    for (int i = 0; i < Capital; ++i)
    {
        password[i] = 'A' + (rand() % 26); // 生成大写字母
    }
    for (int i = Capital; i < Capital + Lower; ++i) 
    {
        password[i] = 'a' + (rand() % 26); // 生成小写字母
    }
    for (int i = Capital + Lower; i < Capital + Lower + Digit; ++i) 
    {
        password[i] = '0' + (rand() % 10); // 生成数字
    }
    for (int i = Capital + Lower + Digit; i < length; ++i) 
    {
        password[i] = other[rand() % strlen(other)]; // 生成其他符号
    }

    // 然后随机打乱生成的密码，以确保字符分布的随机性
    for (int i = 0; i < length - 1; ++i) 
    {
        int j = rand() % (length - i);
        char temp = password[i];
        password[i] = password[j];
        password[j] = temp;
    }
}


// 打乱密码数组
void disrupt(char password[], int length) 
{
    for (int i = 0; i < length; ++i) 
    {
        // 随机选择一个元素与当前元素交换
        int j = rand() % (length - i) + i;

        // 直接交换两个元素的值
        char temp = password[i];
        password[i] = password[j];
        password[j] = temp;
    }
}

// 打印密码
void print(char password[], int length)
{
    for (int i = 0; i < length; ++i) 
        cout << password[i];
}