#include<bits/stdc++.h>
using namespace std;
string solve(int n)
{
    int l=(int )(log2(n));
    return bitset<64>.to_string().substr(64-l-1);
}
int main()
{
 int t;cin>>t;
 while(t--)
 {
cout<<solve(n)<<"\n";
 }
}
    
