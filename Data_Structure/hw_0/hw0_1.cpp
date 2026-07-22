#include <iostream>
#include <iomanip> 
 
using namespace std;
int main() {
    double monthlyIncome[12]; 
    double sum = 0.0; 
    double average; 
 
    for (int i = 0; i < 12; ++i) {
        cin >> monthlyIncome[i];
        sum += monthlyIncome[i]; 
    }
 
    average = sum / 12;
 
    cout << fixed << setprecision(2);
    cout << "?" << average << endl; 
 
    return 0;
}
