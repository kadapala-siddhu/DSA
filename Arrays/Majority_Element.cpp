#include <bits/stdc++.h>
using namespace std;

vector<int> majorityElement(vector<int>& nums) {
    unordered_map<int,int> mp;
    int n=nums.size()/3;

    for(int i=0;i<nums.size();i++)
        mp[nums[i]]++;

    vector<int> ans;
    for(auto &ip : mp)
        if(ip.second>n) ans.push_back(ip.first);

    sort(ans.begin(), ans.end());
    return ans;
}

int main() {
    vector<int>nums={1,2,3,1,1,2,1};

    vector<int>result=majorityElement(nums);

    for(int x : result)
        cout<<x<<" ";

    return 0;
}