#include <bits/stdc++.h>
using namespace std;

int count(const string& s, int i) {
    if (i == s.size()) return 0;

    char c = tolower(s[i]);
    int is = (c == 'a' || c == 'e' || c == 'i' || c == 'o' || c == 'u');

    return is + count(s, i + 1);
}

int main() {
    string s;
    getline(cin, s);

    cout << count(s, 0) << endl;
    return 0;
}
