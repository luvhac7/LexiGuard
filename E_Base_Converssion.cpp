#include<bits/stdc++.h>
using namespace std;
string solve(int n)
{
    int l=(int )(log2(n));
    return bitset<64>(n).to_string().substr(64-l-1);
}
int main()
{
 int t;cin>>t;
 while(t--)
 {
    int n;cin>>n;
cout<<solve(n)<<"\n";
 }
}
    
