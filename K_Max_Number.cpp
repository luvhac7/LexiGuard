#include <bits/stdc++.h>
using namespace std;
using ll=long long;
ll solve(ll n)
{
if(n==1|| n==0) return 1;
else return solve(n-1)*n;
}
int main() {
  int n;cin>>n;
  vector<int>a(n);
  for(int i=0;i<n;i++) cin>>a[i];
  cout<<*max_element(a.begin(),a.end())<<"\n";
}
    


int main()
{

  int n;cin>>n;
  vector<int>a
}