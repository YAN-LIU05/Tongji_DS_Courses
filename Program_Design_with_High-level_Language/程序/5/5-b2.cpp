/* 2352018 –≈06 ¡ı—Â */
#include <iostream>  
using namespace std;

int main() 
{
    const int n = 100;
    int bulb[n] = { 0 }; 

    for (int person = 1; person <= n; ++person) 
    {
        for (int light = person; light <= n; light += person) 
        {  
            bulb[light - 1] = 1 - bulb[light - 1]; 
        }
    }

    for (int i = 0; i < n; ++i) 
    {
        if (bulb[i] == 1)
        { 
            cout << i + 1; 
            if (i + 1 < n)
            {
                cout << " ";
            }
        }
    }
    cout << endl;

    return 0;
}