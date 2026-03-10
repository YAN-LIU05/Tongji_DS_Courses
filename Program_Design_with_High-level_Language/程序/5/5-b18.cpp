/* 2352018 信06 刘彦 */
#include <iostream>

using namespace std;

static const char other[] = "~!@#$%^&*()-_=+[],.?";

// 函数用于检查字符是否属于特定字符集
bool Other_check(char c) 
{
    int Length = sizeof(other) - 1;
    for (int i = 0; i < Length; ++i) 
    {
        if (c == other[i]) 
        {
            return true;
        }
    }
    return false;
}

// 函数用于检查单个密码是否有效
bool check1(const char password[], int length, int Capital, int Lower, int Digit, int Other) 
{
    int capitalCount = 0, lowerCount = 0, digitCount = 0, otherCount = 0, special = 0;

    // 遍历密码字符串，计算各类字符的数量
    for (int i = 0; i < length; ++i)
    {
        if (password[i] >= 'A' && password[i] <= 'Z')
            capitalCount++;
        else if (password[i] >= 'a' && password[i] <= 'z')
            lowerCount++;
        else if (password[i] >= '0' && password[i] <= '9')
            digitCount++;
        else if (Other_check(password[i]))
            otherCount++; 
        else
            special++;
    }

    bool ck1= (capitalCount >= Capital) && (lowerCount >= Lower) && (digitCount >= Digit) && (otherCount >= Other) && (special == 0);
    return ck1;
}

// 检查密码长度和其他条件是否符合要求
bool check2(int length, int Capital, int Lower, int Digit, int Other)
{
    bool ck2_1, ck2_2, ck2_3, ck2_4, ck2_5, ck2_6;
    ck2_1 = length >= 12 && length <= 16;
    ck2_2 = Capital >= 2 && Capital <= length;
    ck2_3 = Lower >= 2 && Lower <= length;
    ck2_4 = Digit >= 2 && Digit <= length;
    ck2_5 = Other >= 2 && Other <= length;
    ck2_6 = Capital + Lower + Digit + Other <= length;
    return ck2_1 && ck2_2 && ck2_3 && ck2_4 && ck2_5 && ck2_6;
}

int main()
{
    int code, Capital, Lower, Digit, Other;
    char password[100]; // 存储单行密码的字符数组
	char sentence[5][20];

    // 读取密码的总长度和各类字符的最小个数
	for (int i = 0; i < 5; i++)  //存第一句
    {
		cin >> sentence[i];
	}
    cin >> code >> Capital >> Lower >> Digit >> Other;
    cin.ignore(); // 忽略换行符

    bool valid = true;
    for (int i = 0; i < 10; ++i) 
    {
        // 清空密码数组以准备读取下一个密码
        for (int j = 0; j < 100; ++j) 
        {
            password[j] = 0;
        }

        // 读取一个密码，直到遇到换行符或达到最大长度
        for (int k = 0; k < code; ++k)
        {
            cin >> password[k];
        }

        // 检查当前密码是否有效
        if (!check1(password, code, Capital, Lower, Digit, Other) || !check2(code, Capital, Lower, Digit, Other)) 
        {
            valid = false;
            break; // 如果发现一个密码无效，则中断循环
        }
    }

    // 输出检查结果
    if (valid)
        cout << "正确" << endl;
    else 
        cout << "错误" << endl;

    return 0;
}