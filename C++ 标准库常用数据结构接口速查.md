# C++ 标准库常用数据结构接口速查

## 1. 顺序容器

### 1.1 vector 动态数组

```cpp
#include <vector>
std::vector<int> v;

v.push_back(10);        // 尾部插入元素
v.pop_back();           // 尾部删除元素
v.size();               // 返回元素个数
v.empty();              // 判断是否为空
v.clear();              // 清空所有元素
v[0];                   // 随机访问，不检查边界
v.at(0);                // 随机访问，边界检查抛异常
v.front();              // 返回第一个元素的引用
v.back();               // 返回最后一个元素的引用
v.begin();              // 返回指向第一个元素的迭代器
v.end();                // 返回指向末尾的迭代器
v.insert(v.begin(), 5); // 在指定位置插入元素
v.erase(v.begin());     // 删除指定位置的元素
v.reserve(100);         // 预分配容量
v.shrink_to_fit();      // 释放多余容量
```

### 1.2 deque 双端队列

```cpp
#include <deque>
std::deque<int> dq;

dq.push_back(10);       // 尾部插入元素
dq.push_front(20);      // 头部插入元素
dq.pop_back();          // 尾部删除元素
dq.pop_front();         // 头部删除元素
dq.front();             // 返回第一个元素的引用
dq.back();              // 返回最后一个元素的引用
dq.size();              // 返回元素个数
dq.empty();             // 判断是否为空
dq.clear();             // 清空所有元素
dq[0];                  // 随机访问，不检查边界
dq.at(0);               // 随机访问，边界检查抛异常
```

### 1.3 list 双向链表

```cpp
#include <list>
std::list<int> lst;

lst.push_back(10);      // 尾部插入元素
lst.push_front(20);     // 头部插入元素
lst.pop_back();         // 尾部删除元素
lst.pop_front();        // 头部删除元素
lst.front();            // 返回第一个元素的引用
lst.back();             // 返回最后一个元素的引用
lst.size();             // 返回元素个数
lst.empty();            // 判断是否为空
lst.clear();            // 清空所有元素
lst.sort();             // 对链表进行排序
lst.unique();           // 删除相邻重复元素
lst.merge(lst2);        // 合并两个已排序链表
lst.reverse();          // 反转链表顺序
lst.remove(10);         // 删除所有值为10的元素
lst.splice(pos, lst2);  // 将另一个链表的节点转移到此链表
```

### 1.4 array 固定大小数组

```cpp
#include <array>
std::array<int, 5> arr = {1, 2, 3, 4, 5};

arr.size();             // 返回数组大小，编译期常量
arr.empty();            // 判断是否为空，C++17起始终返回false
arr.front();            // 返回第一个元素的引用
arr.back();             // 返回最后一个元素的引用
arr[0];                 // 随机访问，不检查边界
arr.at(0);              // 随机访问，边界检查抛异常
arr.fill(0);            // 将所有元素填充为指定值
```

---

## 2. 容器适配器

### 2.1 stack 栈

```cpp
#include <stack>
std::stack<int> s;

s.push(10);             // 入栈，压入元素到栈顶
s.pop();                // 出栈，删除栈顶元素，无返回值
s.top();                // 返回栈顶元素的引用
s.empty();              // 判断栈是否为空
s.size();               // 返回栈中元素个数
// 清空方法: while(!s.empty()) s.pop(); 或 std::stack<int>().swap(s);
```

### 2.2 queue 队列

```cpp
#include <queue>
std::queue<int> q;

q.push(10);             // 入队，在队尾插入元素
q.pop();                // 出队，删除队头元素，无返回值
q.front();              // 返回队头元素的引用
q.back();               // 返回队尾元素的引用
q.empty();              // 判断队列是否为空
q.size();               // 返回队列中元素个数
```

### 2.3 priority_queue 优先队列

```cpp
#include <queue>
std::priority_queue<int> pq;                    // 默认最大堆
std::priority_queue<int, std::vector<int>, std::greater<int>> pq_min;  // 最小堆

pq.push(10);            // 插入元素
pq.pop();               // 删除堆顶元素，无返回值
pq.top();               // 返回堆顶元素的引用，最大或最小
pq.empty();             // 判断优先队列是否为空
pq.size();              // 返回优先队列中元素个数
```

---

## 3. 关联容器

### 3.1 set 有序集合

```cpp
#include <set>
std::set<int> st;

st.insert(10);          // 插入元素
st.erase(10);           // 删除值为10的元素，返回删除个数
st.erase(st.begin());   // 删除迭代器指向的元素
st.find(10);            // 查找元素，返回迭代器，找不到返回end()
st.count(10);           // 返回值为10的元素个数，set中为0或1
st.empty();             // 判断是否为空
st.size();              // 返回元素个数
st.clear();             // 清空所有元素
st.lower_bound(10);     // 返回第一个不小于10的迭代器
st.upper_bound(10);     // 返回第一个大于10的迭代器
st.equal_range(10);     // 返回lower_bound和upper_bound的pair对
```

### 3.2 multiset 有序多重集合

```cpp
#include <set>
std::multiset<int> ms;

ms.insert(10);          // 插入元素，允许重复
ms.erase(10);           // 删除所有值为10的元素
ms.find(10);            // 查找元素，返回第一个匹配的迭代器
ms.count(10);           // 返回值为10的元素个数，可能大于1
ms.empty();             // 判断是否为空
ms.size();              // 返回元素个数
ms.clear();             // 清空所有元素
ms.lower_bound(10);     // 返回第一个不小于10的迭代器
ms.upper_bound(10);     // 返回第一个大于10的迭代器
ms.equal_range(10);     // 返回lower_bound和upper_bound的pair对
```

### 3.3 map 有序映射

```cpp
#include <map>
std::map<std::string, int> mp;

mp["apple"] = 5;        // 插入或修改，键不存在时默认构造插入
mp.at("apple") = 10;    // 访问或修改，键不存在时抛out_of_range异常
mp.insert({"banana", 3});   // 插入键值对
mp.emplace("cherry", 7);    // 原位构造插入键值对，更高效
mp.find("apple");       // 查找键，返回迭代器，找不到返回end()
mp.count("apple");      // 返回键的个数，map中为0或1
mp.erase("apple");      // 删除键及对应的值
mp.empty();             // 判断是否为空
mp.size();              // 返回键值对个数
mp.clear();             // 清空所有键值对
// 遍历: for(auto& p : mp) { p.first; p.second; }
```

### 3.4 multimap 有序多重映射

```cpp
#include <map>
std::multimap<std::string, int> mmp;

mmp.insert({"apple", 5});   // 插入键值对，允许键重复
mmp.insert({"apple", 3});   // 同一个键可对应多个值
mmp.find("apple");          // 查找键，返回第一个匹配的迭代器
mmp.count("apple");         // 返回键的个数，可能大于1
mmp.erase("apple");         // 删除所有匹配该键的键值对
mmp.empty();                // 判断是否为空
mmp.size();                 // 返回键值对个数
mmp.clear();                // 清空所有键值对
mmp.lower_bound("apple");   // 返回第一个不小于键的迭代器
mmp.upper_bound("apple");   // 返回第一个大于键的迭代器
mmp.equal_range("apple");   // 返回lower_bound和upper_bound的pair对
```

---

## 4. 无序容器

### 4.1 unordered_set 哈希集合

```cpp
#include <unordered_set>
std::unordered_set<int> us;

us.insert(10);          // 插入元素
us.erase(10);           // 删除值为10的元素
us.find(10);            // 查找元素，返回迭代器，找不到返回end()
us.count(10);           // 返回值为10的元素个数，为0或1
us.empty();             // 判断是否为空
us.size();              // 返回元素个数
us.clear();             // 清空所有元素
us.reserve(100);        // 预分配桶数，减少rehash
us.rehash(100);         // 设置桶数
us.bucket_count();      // 返回桶的数量
us.load_factor();       // 返回负载因子
```

### 4.2 unordered_multiset 哈希多重集合

```cpp
#include <unordered_set>
std::unordered_multiset<int> ums;

ums.insert(10);         // 插入元素，允许重复
ums.insert(10);         // 可插入多个相同值
ums.erase(10);          // 删除所有值为10的元素
ums.find(10);           // 查找元素，返回第一个匹配的迭代器
ums.count(10);          // 返回值为10的元素个数，可能大于1
ums.empty();            // 判断是否为空
ums.size();             // 返回元素个数
ums.clear();            // 清空所有元素
ums.reserve(100);       // 预分配桶数
```

### 4.3 unordered_map 哈希映射

```cpp
#include <unordered_map>
std::unordered_map<std::string, int> ump;

ump["apple"] = 5;       // 插入或修改，键不存在时默认构造插入
ump.at("apple") = 10;   // 访问或修改，键不存在时抛out_of_range异常
ump.insert({"banana", 3});  // 插入键值对
ump.emplace("cherry", 7);   // 原位构造插入键值对，更高效
ump.find("apple");      // 查找键，返回迭代器，找不到返回end()
ump.count("apple");     // 返回键的个数，为0或1
ump.erase("apple");     // 删除键及对应的值
ump.empty();            // 判断是否为空
ump.size();             // 返回键值对个数
ump.clear();            // 清空所有键值对
ump.reserve(100);       // 预分配桶数，减少rehash
ump.rehash(100);        // 设置桶数
ump.bucket_count();     // 返回桶的数量
ump.load_factor();      // 返回负载因子
// 遍历: for(auto& p : ump) { p.first; p.second; }
```

### 4.4 unordered_multimap 哈希多重映射

```cpp
#include <unordered_map>
std::unordered_multimap<std::string, int> ummp;

ummp.insert({"apple", 5});  // 插入键值对，允许键重复
ummp.insert({"apple", 3});  // 同一个键可对应多个值
ummp.find("apple");         // 查找键，返回第一个匹配的迭代器
ummp.count("apple");        // 返回键的个数，可能大于1
ummp.erase("apple");        // 删除所有匹配该键的键值对
ummp.empty();               // 判断是否为空
ummp.size();                // 返回键值对个数
ummp.clear();               // 清空所有键值对
ummp.reserve(100);          // 预分配桶数
```

---

## 5. 通用操作速查表

| 操作 | vector | deque | list | array | stack | queue | priority_queue | set/map | unordered_set/map |
|------|--------|-------|------|-------|-------|-------|----------------|---------|-------------------|
| 插入 | push_back | push_back/front | push_back/front | 赋值初始化 | push | push | push | insert | insert |
| 删除 | pop_back | pop_back/front | pop_back/front | - | pop | pop | pop | erase | erase |
| 访问 | []/at | []/at | - | []/at | top | front/back | top | 迭代器 | 迭代器 |
| 大小 | size | size | size | size | size | size | size | size | size |
| 判空 | empty | empty | empty | empty | empty | empty | empty | empty | empty |
| 清空 | clear | clear | clear | - | 循环pop | 循环pop | 循环pop | clear | clear |
| 查找 | find算法 | find算法 | find算法 | find算法 | - | - | - | find | find |
| 计数 | count算法 | count算法 | count算法 | count算法 | - | - | - | count | count |

---

## 6. 注意事项

关于count方法的返回值
- set, map, unordered_set, unordered_map中的count返回0或1
- multiset, multimap, unordered_multiset, unordered_multimap中的count可返回大于1

关于stack和queue的清空
- 适配器容器无clear方法
- 清空方式: while(!s.empty()) s.pop()
- 或通过交换: std::stack<int>().swap(s)

关于map和unordered_map的访问
- operator[]会在键不存在时插入默认值
- at()在键不存在时抛出std::out_of_range异常
- 建议先用count或find检查键是否存在

遍历时删除元素的安全写法
- for(auto it = c.begin(); it != c.end(); ) { if(条件) it = c.erase(it); else ++it; }
- 关联容器erase返回迭代器，顺序容器erase也返回迭代器