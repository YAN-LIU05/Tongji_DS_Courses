/* 2352018 大数据 刘彦 */
#include <iostream>
/* --如果某编译器有需要，此处允许按条件编译的格式加入头文件 --*/

using namespace std;

int main()
{
    char a[80];

#if defined(__MINGW32__) || defined(__MINGW64__) // Dev-C++
    gets(a);
#elif defined(_MSC_VER) // VS2022
    gets_s(a, sizeof(a)); 
#elif defined(__linux__) // Linux
    fgets(a, sizeof(a), stdin); 
#endif

    cout << a << endl;
	return 0;
}