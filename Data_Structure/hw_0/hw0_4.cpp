#include <iostream>
using namespace std;
 
long long computeValue(const char* str) {
    long long n = 0;
    int i = 0;
    while (true) {
        if (str[i] == '\r' || str[i] == '\n' || str[i] == 0)
            break;
        else if (str[i] != ' ')
            n += (str[i] - 64) * (i + 1);
        i++;
    }
    return n;
}
 
int main()
{
    while (true)
    {
        char str[1000];
        cin.getline(str, 1000);
        if (str[0] == '#')
            break;
        else
        {
            long long result = computeValue(str);
            cout << result << endl;
        }
    }
    return 0;
}
