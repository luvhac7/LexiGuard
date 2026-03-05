#include <bits/stdc++.h>
using namespace std;


void solve(int lvl,int n)
{
    if(lvl==n) return;
    for(int i=0;i<lvl;i++)
        cout<<' ';
    for(int i=0;i<2*(n-lvl)-1;i++)
        cout<<'*';
    cout<<'\n';
    solve(lvl+1,n);
}

int main() {
    int n;
    cin >> n;
    solve(0, n);
    return 0;
}














