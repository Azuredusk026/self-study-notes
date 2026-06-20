# 算法基础与递归枚举：从逻辑重构到工程实践

## 一、 核心知识点与原理剖析

### 1. 算法的定义与本质
* **新课三连问**：学习一门新课程时，首先应明确的三个根本性问题是：**是什么**、**为什么要学**、**怎么去学**。
* **维基百科定义**：在数学与计算机科学中，算法是一个被定义好的、计算机可执行的、包含有限步骤或次序的指示，常用于计算、数据处理和自动推理。
* **本质剖析**：
  * 算法在本质上是**一门数学学科**，而非纯粹的计算机学科。在程序设计语言和电子计算机问世之前，算法的理论与逻辑就已经存在。
  * 算法的本质是**描述计算过程的逻辑与步骤**，它独立于具体的实现代码。计算机的出现只是让算法能够**自动化地运行**，这类似于工业生产中“使用电动挖矿机和传送带对传统手工采煤炼铁的自动化替代”。

---

### 2. 经典算法设计问题引入

#### (1) 迷宫寻路问题 (触摸墙壁法)
* **算法描述**：
  1. 进入迷宫入口。
  2. 伸出右手（或左手）。
  3. 摸着一侧的墙面。
  4. 在手不放开、不离开墙面的前提下，一直往前走，直至走到终点。
* **局限性**：该算法无法解决**非单连通（Non-simply connected）或存在循环回路的迷宫**。
  * *原理解析*：如果起点与终点不连通，或者终点位于迷宫中央的闭合环路内部（即终点被一圈环状通道包围），使用摸右墙法会导致角色在环路上不断循环打转，永远无法脱困并到达终点。

#### (2) 16枚硬币称重问题 (二分与三分)
* **问题描述**：在 16 枚硬币中找出唯一一枚质量较轻的假币，唯一的工具是一台天平。
* **二分法（Bisection Method）**：
  * 将硬币平均分成两堆，用天平称量，留下更轻的那一堆。
  * 判定当前堆是否仅剩一枚：若剩一枚则找到；若多于一枚，则继续重复上述平分与称量过程。
  * **复杂度**：对于 $n$ 枚硬币，最坏情况下需要进行 $\log_2 n$ 次比较。对于 16 枚硬币，需要比较 $\log_2 16 = 4$ 次。
* **三分法（Trisection Method）**：
  * 将硬币平均分成三堆（标记为 A、B、C），用天平称量 A 和 B 的重量。
  * 若 A、B 平衡，则假币在 C 中；若 A 比 B 轻，则假币在 A 中；反之在 B 中。
  * **效率对比**：三分法相比二分法，每次可以排除大约 2/3 的硬币，**比较次数更少**，在时间上更快。对于 $n$ 枚硬币，最坏情况下需要 $\log_3 n$ 次比较。
* **任意数量硬币的通用推广**：
  * 如果硬币总数 $n$ 不能被 2 整数（例如奇数个），处理方式是：**先取出一枚硬币留空，将剩余偶数个硬币平均分成两堆**进行称量。
  * 若天平平衡，则取出的那枚即为假币；若天平不平衡，则假币必定在较轻的那一堆中，继续进行二分搜索。
  * **平均次数与期望次数**：若在第一步就正好把假币作为“取出的那一枚”剔除，则仅需 1 次比较即可找到假币。但在 $n$ 极大时，这种特殊情况发生的概率极小。从期望次数或平均次数来看，整体的复杂度依旧是 $O(\log n)$ 级别。

---

### 3. 算法评价标准（复杂度分析）
算法优劣的评价指标主要有两个：**时间效率**和**空间效率**。

#### (1) 空间效率
* 由算法执行时所消耗的内存空间决定，通常通过算法中开辟的数组大小和维度来体现。
* *示例*：解决同一问题，一个算法开辟了一维数组（空间为 $O(n)$），而另一个算法开辟了二维数组（空间为 $O(n^2)$），后者的空间效率显著低于前者。

#### (2) 时间效率
衡量算法运行速度的关键指标。在描述时间效率时，**对数（$\log$）** 具有至关重要的地位。
* **对数（$\log$）的通俗理解**：在计算机科学中，$\log n$ 默认以 2 为底（即 $\log_2 n$）。它直观地表示**一个规模为 $n$ 的问题，通过每次折半（二分），需要分割多少次才能缩减为 1**。
  * 当数据规模 $n = 10^5$ 时，线性暴力查找需要比较约 $10^5$ 次，而对数级算法（如二分查找）仅需约 $\log_2(10^5) \approx 17$ 次，两者的效率相差数千倍。
* **排序算法的时间复杂度对比**：
  * **排序定义**：输入为 $n$ 个数的序列 $\langle A_1, A_2, ..., A_n \rangle$，输出为满足 $A'_1 \le A'_2 \le ... \le A'_n$ 的序列排列。
  * **插入排序（Insertion Sort）**：硬件指令消耗大约为 $C_1 \cdot n^2$（$C_1$ 为与代码写法及指令复杂度相关的常数）。
  * **归并排序（Merge Sort）**：硬件指令消耗大约为 $C_2 \cdot n \log n$（$C_2$ 为常数）。
  * **软硬件综合效率对比实例**：
    * 计算机 A：主频极高，每秒执行 $10^{10}$ 条指令；运行优化良好的插入排序（常数 $C_1 = 2$）。
    * 计算机 B：主频较低，每秒仅执行 $10^7$ 条指令（性能相差 1000 倍）；运行效率较低的归并排序（常数 $C_2 = 50$，程序员水平较差）。
    * 排序规模 $n = 10^7$ 时的时间开销：
      * **计算机 A（插入排序）**：
        $$t_A = \frac{2 \times (10^7)^2}{10^{10}} = 20000 \text{ 秒} \approx 5.5 \text{ 小时}$$
      * **计算机 B（归并排序）**：
        $$t_B = \frac{50 \times 10^7 \times \log_2(10^7)}{10^7} \approx 50 \times 24 = 1200 \text{ 秒} \approx 20 \text{ 分钟}$$
      * **结论**：硬件性能的差距（1000倍）和代码实现的常数项优化（25倍），在算法时间复杂度（$n^2$ 对比 $n \log n$）的决定性差距面前微不足道。**设计并使用优秀的算法是提升效率最核心的手段**。

---

### 4. 枚举法剖析

#### (1) 笛卡尔积与解空间
* **笛卡尔积（Cartesian Product）**：
  * 设有集合 $A$ 和 $B$，它们的笛卡尔积表示为 $A \times B$，是所有有序对 $(a, b)$ 构成的集合，其中 $a \in A, b \in B$。若 $A$ 和 $B$ 为有限集，则其基数（大小）为 $|A| \times |B|$。
  * 推广至 $n$ 个集合的笛卡尔积，其结果为一个 $n$ 元组的集合，基数为所有集合大小的乘积。
* **解空间（Solution Space）**：
  * 问题的所有可能解构成的集合，它在数学上表现为**所有相关变量值域的笛卡尔积**。
  * 解空间中包含了**合法解/最优解**以及**非法解**。
  * *示例*：对于方程 $3x - 2y = 1$（$x, y$ 均为正整数），其解空间就是正整数集与正整数集的笛卡尔积 $\mathbb{Z}^+ \times \mathbb{Z}^+$。
* **枚举法（Enumeration Method）**：
  * **核心定义**：列举解空间中的所有元素，并对其逐一判定，以寻找符合约束的合法解或全局最优解。
  * **决定枚举规模的三个关键因素**：
    1. **变量的个数**：决定了解空间的维度（维数）。在代码实现中，**维数通常与算法嵌套的循环层数相等**。
    2. **变量的值域**：确定了每次循环枚举的起始与终止边界。
    3. **笛卡尔积的基数**：等于值域的大小相乘，决定了算法的总循环迭代次数。

#### (2) 经典枚举问题及解空间设计

##### 问题一：乱码单词查找（模式匹配）
* **问题描述**：在一个大字符串 $S$ 中查找目标单词 $W$（例如 "Stack"），返回其首次出现的 1-based 起始下标，未找到则返回 -1。
* **解空间设计**：一维解空间，即 $S$ 中所有可能的起始下标 $i$（范围为 $[0, |S| - |W|]$）。
* **合法性判定**：通过内层辅助循环判定从起始位置 $i$ 开始的子串是否与 $W$ 完全相等。
* **高效算法拓展**：**KMP 算法（Knuth-Morris-Pratt）**。它通过预处理模式串 $W$ 的前缀和后缀最大匹配长度，在失配时可以直接滑动到下一个可能匹配的位置，从而跳过大量无用的中间起始位置枚举，将时间复杂度降低到 $O(|S| + |W|)$。

##### 问题二：最长回文子串
* **问题描述**：从字符串中找出最长的回文子串（例如 "Banana" 的最长回文子串为 "Anana"）。
* **解空间设计 1**：以子串的左边界下标 $i$ 和右边界下标 $j$ 作为变量。解空间由满足 $0 \le i \le j < n$ 的所有整数对 $(i, j)$ 构成，属于二维解空间，大小为 $O(n^2)$。
* **解空间设计 2**：以子串的左边界起始坐标 $i$ 和子串长度 $k$ 作为变量。
* **枚举顺序优化**：
  * 采用**解空间设计 2**，将**长度 $k$ 作为外层循环**，从最长长度 $n$ 递减枚举到 1；将**起点 $i$ 作为内层循环**。
  * 在该枚举顺序下，首次检验通过的合法回文子串必然是全局最长的，可以直接返回，从而避免了遍历整个解空间。
  * **重要逻辑注意**：如果颠倒内外层循环，将起点 $i$ 作为外层，长度 $k$ 作为内层，则无法保证首次遇到的回文串是最长回文串，算法必须遍历所有情况并用最大值变量进行更新。

##### 问题三：分数分解
* **问题描述**：对于确定的正整数 $k$，求方程 $\frac{1}{k} = \frac{1}{x} + \frac{1}{y}$ 且满足 $x \ge y \ge k$ 的所有正整数解对。
* **值域数学约束推导**：
  * 这是一个二维解空间问题，直接枚举 $x$ 和 $y$ 到无穷大是不可行的，必须进行范围缩减。
  * 因为 $x \ge y \implies \frac{1}{x} \le \frac{1}{y}$，因此：
    $$\frac{1}{k} = \frac{1}{x} + \frac{1}{y} \le \frac{2}{y} \implies y \le 2k$$
  * 又因为 $x > 0 \implies \frac{1}{y} < \frac{1}{k} \implies y > k$。
  * 综上，变量 $y$ 的确定值域为 $[k+1, 2k]$。
* **维度缩减**：
  * 由于确定了 $y$ 的值，根据方程可以直接计算出 $x$：
    $$x = \frac{k \cdot y}{y - k}$$
  * 这意味着该问题可以被退化为一维枚举：只需枚举 $y \in [k+1, 2k]$，计算 $x$，若 $x$ 为整数且满足 $x \ge y$，则是一组合法解。

---

### 5. 递归与回溯算法

#### (1) 递归解决“动态循环层数”问题
* **引入原因**：在某些枚举问题（如全排列）中，解空间的维度（即循环的嵌套层数）取决于输入的参数 $n$。由于代码中的 `for` 循环嵌套层数是静态编译的，无法根据运行期变量动态增减，因此必须引入**递归（Recursion）**来动态模拟未知层数的嵌套循环。
* **递归函数的核心三要素**：
  1. **边界条件（Base Case）**：用于控制递归的深度。当递归调用达到限制条件（如已经填满了 $n$ 个位置，即 $idx > n$）时，不再进行更深层次的自我调用，直接处理/输出结果并返回。
  2. **递归体（Recursive Body）**：在当前层通过 `for` 循环枚举当前位置所有可行的候选值，并调用自身传入 `idx + 1`，将计算流程推进到下一层嵌套。
  3. **回溯恢复（Backtracking State Reset）**：在递归调用返回后，必须将当前层对全局或共享状态（如标记数组 `used`）所做的修改**重置回初始状态**，以防止污染后续其他并行分支的决策路径。
* **递归树（Recursion Tree）**：递归调用过程在逻辑上展开为一棵树（决策树）。树的深度对应递归层数，分叉对应每一层的选择。

#### (2) 经典递归与回溯问题

##### 问题一：全排列 (Full Permutation)
* **问题描述**：输出 1 到 $n$ 的所有无重复数字排列。
* **解空间**：$n$ 维解空间，每一维的值域为 $[1, n]$，约束条件为任意两维的数字不能重复。
* **算法设计**：
  * 维护一个全局标记数组 `used`（记录数值是否被当前排列占用）以及保存当前排列的数组 $p$。
  * 递归函数 `Permutation(idx)` 表示正在确定排列的第 `idx` 位。
  * 遍历可能填入的数字 $i \in [1, n]$，若 `used[i] == false`，则将其填入并标记为已使用，随后递归执行 `Permutation(idx + 1)`，**执行完毕后必须进行回溯恢复，将 `used[i]` 重新设为 `false`**。

##### 问题二：糖果分解 (整数拆分)
* **问题描述**：将整数 $n$ 分解为若干正整数相加的形式，输出所有不重复的分解方案，按字典序排序（例如 $3 = 1+1+1$、$1+2$、$3$）。
* **去重设计**：
  * 类似 $1+2$ 和 $2+1$ 属于同一种划分。为了实现字典序且去重，要求划分中的数**单调递增**，即后一个数必须大于等于前一个数。
  * **递归体参数设计**：在递归函数中传入上一次拆分出来的数字 `lastNum`。在当前层枚举拆分数值时，`for` 循环的起点必须设为 `lastNum`，从而保证了生成的序列天然满足 $a_i \ge a_{i-1}$ 的有序性。

##### 问题三：装箱问题 (Knapsack 变种)
* **问题描述**：箱子容量为 $V$，有 $n$ 个行李，每个行李有体积 $v_i$。求如何装箱使箱子的剩余浪费空间最小。
* **贪心算法的反例**：
  * 贪心策略（“大行李先装入”）无法求得最优解。
  * *反例*：箱子容量 $V = 10$，三个行李体积分别为 $9, 8, 2$。
    * 若按贪心策略，优先装入体积最大的 $9$，剩余空间为 1，无法装入其他，浪费空间为 1。
    * 实际最优解为装入 $8$ 和 $2$，箱子刚好装满，浪费空间为 0。
* **基于递归的完全枚举设计**：
  * 为了避免组合重复枚举（即选了 $A$ 和 $B$ 之后，又在后续搜索中选了 $B$ 和 $A$），需要保证每次只向后检索行李。
  * 传入参数 `lastItemIndex`，当前层的循环起点设定为 `lastItemIndex + 1`，保证行李选择顺序的单调性。

---

## 二、 重点术语与概念解析

* **算法（Algorithm）**：描述计算过程的、由有限步骤或次序构成的逻辑方案，具有定义明确、计算机可执行的特征。
* **单连通与非单连通迷宫（Simply / Non-simply Connected Maze）**：
  * **单连通迷宫**：内部不存在闭合环路的迷宫，等价于拓扑学中的无环图，可以使用简单的“摸右墙法”遍历。
  * **非单连通迷宫**：内部包含环路、岛屿或独立区域的迷宫。“摸右墙法”在此类迷宫中容易陷入局部环路而无法到达终点。
* **二分法与三分法（Binary / Ternary Search）**：通过每次将搜索区间分别平分为 2 等份或 3 等份来缩小候选集范围的算法。在查找假币问题中，三分法比二分法收敛得更快，但两者的渐进时间复杂度均为对数级 $O(\log n)$。
* **对数（Logarithm, $\log$）**：在计算机算法分析中，通常特指以 2 为底的对数 $\log_2$。指将大小为 $n$ 的数连续除以 2 直到为 1 的次数。
* **笛卡尔积（Cartesian Product）**：由两个或多个集合的所有可能的有序元组组成的集合。若集合大小分别为 $m$ 和 $n$，其笛卡尔积的大小为 $m \times n$。
* **解空间（Solution Space）**：由问题的所有候选解（无论是否合法）所构成的完整集合。枚举算法就是在该空间中搜索目标状态的过程。
* **KMP 算法（Knuth-Morris-Pratt Algorithm）**：一种用于解决字符串匹配问题的线性时间复杂度算法，其精髓在于利用已知部分匹配的前后缀信息，避免匹配指针回溯。
* **回溯（Backtracking）**：在深度优先搜索（DFS）或递归探索决策树时，当一条路径无法继续走通，返回上一个决策点时，将之前修改的全局或局部状态恢复至原状的操作。
* **字典序（Lexicographical Order）**：一种基于字母表顺序排列字符串或序列的标准排序方法。例如序列 $[1, 1, 1]$ 在字典序上小于 $[1, 2]$。
* **贪心算法（Greedy Algorithm）**：在解决问题时，每一步都采取当前状态下的局部最优选择，期望借此达到全局最优的策略。但在诸如装箱等 NP 难问题上，通常无法保证得到全局最优解。

---

## 三、 工程经验与避坑指南

### 1. 变量命名规范
* **避坑警示**：在写算法或进行练习时，常有同学习惯性使用简单字母（如 `a`, `b`, `c`, `d`, `e`）来命名数组和核心变量。这虽然在简短的单文件算法中看似方便，但在大型工程项目（如使用 C# 编写的 Unity 游戏项目）中是极坏的习惯，会导致代码可读性极低，极难维护。
* **工程建议**：即使是算法练习，也应当使用具有明确物理意义的命名。例如，用 `remainBeans`（剩余怪味豆）代替 `a`，用 `isVisited` 代替 `f`，用 `lastSelectedNumber` 代替 `last`。

### 2. 评测系统（Evaluator）兼容性陷阱
* **语法糖局限**：在线评测服务器（云端测试服务器）所使用的编译器版本可能较旧，没有本地 IDE 那样先进的“语法糖”支持。
* **避坑实践**：
  * **避免在 C# 中滥用 LINQ**（如 `list.Max()` 或快捷转换方法 `ConvertAll` 等），否则非常容易在云端评测时报出编译错误或运行时异常（如 `System.FormatException`）。应老老实实编写传统的循环结构进行最大值查找和类型转换。
  * **规避顶级语句（Top-level statements）**。新版 C# 编译器支持不写 `namespace` 和 `Class Program` 直接编写逻辑，但老版云端编译器不认识这种语法。必须严格按照老版本格式声明命名空间和主类：
    ```csharp
    using System;

    namespace AlgorithmClass
    {
        class Program
        {
            static void Main(string[] args)
            {
                // 逻辑代码
            }
        }
    }
    ```
  * **注意命名空间引用**：在本地开发时，IDE 可能会默认隐式引用 `System` 命名空间。然而在云端提交时，**必须显式写明 `using System;`**，否则所有类似 `Console.ReadLine()` 等控制台语句都将报出 `Console does not exist` 的编译错误。

### 3. WA (答案错误) 调试手段
* **中间状态打印**：当代码在评测系统中通过了样例但在大样本数据下返回了 WA（Wrong Answer），最有效的调试手段是使用 `Console.WriteLine` 在循环或递归的中间步骤输出核心变量的值（例如把解析的数组逐个打印出来，检查是否由于空格分割导致解析异常）。
* **提交前置清理**：在确认代码逻辑无误后，**务必在最终点击提交前将所有的调试打印语句（`Console.WriteLine` / `Console.Write`）删除或注释掉**。因为云端评测机是通过比对你的控制台总输出与标准答案文件来判定正确性的，多余的调试日志会被判定为答案错误。

### 4. 递归与回溯的常见逻辑漏洞
* **状态重置（回溯）缺失**：这是递归程序中最经典的 Bug。如果一个变量在递归进入下一层时被标记为 `true`（例如排列中该数字已被占用），但在递归退出时没有恢复为 `false`，会导致后续的决策分支无法再使用这个变量，表现为丢失大量合法解或提前终止。
* **栈溢出（Stack Overflow）**：若忘记编写边界终止条件，或者边界终止条件的判定范围写错（例如在糖果拆分问题中只判定了 `remain == 0`，却因数值递减越过了 0 导致 `remain` 变成负数），会导致递归树无限向下生长，最终由于系统调用栈空间耗尽而崩溃。

### 5. 数据范围与边界溢出
* **整型溢出**：在涉及乘除法运算的题目（如分数分解 $\frac{1}{k} = \frac{1}{x} + \frac{1}{y}$ 转换出的分子分母计算时）中，如果输入 $k$ 的绝对值较大，在进行 `k * y` 乘法计算时会极易超出 32 位整型 `int` 的表示上限（约 $\pm 2.14 \times 10^9$）。
* **防范机制**：在涉及可能导致大数相乘的步骤时，应在计算前将变量强转为 64 位整型（C# 中使用 `long` 或 `Int64`）以防计算溢出。
  ```csharp
  long numerator = (long)k * y; // 使用 long 承接乘法结果，防止溢出
  ```
* **1-based 还是 0-based 下标转换**：
  * 题目输出通常面向人类阅读，下标习惯从 1 开始。但各种编程语言的数组或字符串下标默认从 0 开始。
  * 在输出匹配索引或子串起始位置时，记得进行加一转换；同时注意对于没有找到解（输出 -1）的边界情况，不可无脑进行加一操作，必须加上特判逻辑。

---

## 四、 课后算法习题核心代码实现 (C#)

### 1. 怪味豆最大值寻找 (1001)
```csharp
using System;

namespace AlgorithmClass
{
    class Program
    {
        static void Main(string[] args)
        {
            // 读入第一行，代表怪味豆的数量 n
            string firstLine = Console.ReadLine();
            if (string.IsNullOrEmpty(firstLine)) return;
            int n = int.Parse(firstLine);

            // 读入第二行，代表每颗怪味豆的评分
            string secondLine = Console.ReadLine();
            if (string.IsNullOrEmpty(secondLine)) return;
            string[] stringTokens = secondLine.Split(' ');
            
            int[] ratings = new int[n];
            for (int i = 0; i < n; i++)
            {
                ratings[i] = int.Parse(stringTokens[i]);
            }

            // 核心算法：遍历寻找最大值
            int maxRating = int.MinValue;
            for (int i = 0; i < n; i++)
            {
                if (ratings[i] > maxRating)
                {
                    maxRating = ratings[i];
                }
            }

            // 输出最终结果
            Console.WriteLine(maxRating);
        }
    }
}
```

### 2. 乱码单词匹配 (1002)
```csharp
using System;

namespace AlgorithmClass
{
    class Program
    {
        static void Main(string[] args)
        {
            // 读入长文本和模式单词
            string text = Console.ReadLine();
            string pattern = Console.ReadLine();
            
            if (text == null || pattern == null) return;

            int index = FindPattern(text, pattern);
            Console.WriteLine(index);
        }

        static int FindPattern(string text, string pattern)
        {
            int n = text.Length;
            int m = pattern.Length;

            // 枚举解空间：起始下标 i 
            for (int i = 0; i <= n - m; i++)
            {
                bool match = true;
                // 验证可行性
                for (int j = 0; j < m; j++)
                {
                    if (text[i + j] != pattern[j])
                    {
                        match = false;
                        break;
                    }
                }
                if (match)
                {
                    // 题面要求的下标是从 1 开始的，所以需要加一
                    return i + 1;
                }
            }
            return -1; // 未匹配到返回 -1
        }
    }
}
```

### 3. 最长回文子串 (1004)
```csharp
using System;

namespace AlgorithmClass
{
    class Program
    {
        static void Main(string[] args)
        {
            string s = Console.ReadLine();
            if (string.IsNullOrEmpty(s)) return;

            string result = GetLongestPalindrome(s);
            Console.WriteLine(result);
        }

        static string GetLongestPalindrome(string s)
        {
            int n = s.Length;

            // 优化解空间枚举方式：从最长长度开始向下枚举
            for (int len = n; len >= 1; len--)
            {
                // 枚举起始位置 i
                for (int i = 0; i <= n - len; i++)
                {
                    if (IsPalindrome(s, i, i + len - 1))
                    {
                        // 首次找到的即为最长回文子串
                        return s.Substring(i, len);
                    }
                }
            }
            return "";
        }

        static bool IsPalindrome(string s, int left, int right)
        {
            while (left < right)
            {
                if (s[left] != s[right])
                    return false;
                left++;
                right--;
            }
            return true;
        }
    }
}
```

### 4. 分数分解 (1005)
```csharp
using System;
using System.Collections.Generic;

namespace AlgorithmClass
{
    class Program
    {
        static void Main(string[] args)
        {
            string input = Console.ReadLine();
            if (string.IsNullOrEmpty(input)) return;
            int k = int.Parse(input);

            List<string> results = new List<string>();

            // 枚举 y 范围：[k + 1, 2k]
            for (int y = k + 1; y <= 2 * k; y++)
            {
                // 1/k = 1/x + 1/y 转换得 x = (k * y) / (y - k)
                // 为防止乘法溢出，在此使用 long 类型
                long numerator = (long)k * y;
                long denominator = y - k;

                if (numerator % denominator == 0)
                {
                    long x = numerator / denominator;
                    if (x >= y)
                    {
                        results.Add($"1/{k} = 1/{x} + 1/{y}");
                    }
                }
            }

            foreach (var res in results)
            {
                Console.WriteLine(res);
            }
        }
    }
}
```

### 5. 全排列生成 (1006)
```csharp
using System;

namespace AlgorithmClass
{
    class Program
    {
        static int n;
        static int[] p;       // 记录排列结果
        static bool[] used;   // 标记数字占用情况

        static void Main(string[] args)
        {
            string input = Console.ReadLine();
            if (string.IsNullOrEmpty(input)) return;
            n = int.Parse(input);

            p = new int[n + 1];
            used = new bool[n + 1];

            // 从第 1 位开始递归枚举
            Permutation(1);
        }

        static void Permutation(int idx)
        {
            // 边界条件：当枚举位数超出 n，说明已得到一组全排列
            if (idx > n)
            {
                for (int i = 1; i <= n; i++)
                {
                    Console.Write(p[i] + (i == n ? "" : " "));
                }
                Console.WriteLine();
                return;
            }

            // 递归体
            for (int i = 1; i <= n; i++)
            {
                if (!used[i])
                {
                    p[idx] = i;       // 选择当前数字
                    used[i] = true;   // 标记占用
                    
                    Permutation(idx + 1); // 深入下一层

                    used[i] = false;  // 回溯：重置状态
                }
            }
        }
    }
}
```

### 6. 糖果分解 / 整数拆分 (1007)
```csharp
using System;
using System.Collections.Generic;

namespace AlgorithmClass
{
    class Program
    {
        static int n;
        static List<int> path = new List<int>(); // 存储拆分方案的数值路径

        static void Main(string[] args)
        {
            string input = Console.ReadLine();
            if (string.IsNullOrEmpty(input)) return;
            n = int.Parse(input);

            // 递归起点：剩余值 n，初始最小值下限 1
            Partition(n, 1);
        }

        static void Partition(int remain, int lastNum)
        {
            // 边界条件：剩余凑值刚好为 0，输出有效划分
            if (remain == 0)
            {
                for (int i = 0; i < path.Count; i++)
                {
                    Console.Write(path[i] + (i == path.Count - 1 ? "" : " + "));
                }
                Console.WriteLine();
                return;
            }

            // 递归体：通过限定起点为 lastNum，确保拆分项非降序，天然去重
            for (int i = lastNum; i <= remain; i++)
            {
                path.Add(i);
                Partition(remain - i, i);         // 递归：更新剩余凑值，下限更新为当前数 i
                path.RemoveAt(path.Count - 1);    // 回溯：移除当前尝试值
            }
        }
    }
}
```

### 7. 行李装箱问题 (1008)
```csharp
using System;

namespace AlgorithmClass
{
    class Program
    {
        static int totalCapacity;
        static int n;
        static int[] volumes;
        static int minRemainingSpace;

        static void Main(string[] args)
        {
            // 读入箱子容量 V
            string firstLine = Console.ReadLine();
            if (string.IsNullOrEmpty(firstLine)) return;
            totalCapacity = int.Parse(firstLine);

            // 读入物品数量 n
            string secondLine = Console.ReadLine();
            if (string.IsNullOrEmpty(secondLine)) return;
            n = int.Parse(secondLine);

            volumes = new int[n];
            for (int i = 0; i < n; i++)
            {
                string itemVal = Console.ReadLine();
                if (!string.IsNullOrEmpty(itemVal))
                {
                    volumes[i] = int.Parse(itemVal);
                }
            }

            // 初始化浪费空间最大为箱子自身容量
            minRemainingSpace = totalCapacity;

            // 启动递归查找：初始剩余容量为 totalCapacity，起始考虑索引为 0
            Solve(totalCapacity, 0);

            Console.WriteLine(minRemainingSpace);
        }

        static void Solve(int currentCapacity, int lastItemIndex)
        {
            // 每次进入分支，尝试更新浪费空间极小值
            if (currentCapacity < minRemainingSpace)
            {
                minRemainingSpace = currentCapacity;
            }

            // 递归体：为了防止组合重复，只从 lastItemIndex 开始向后枚举
            for (int i = lastItemIndex; i < n; i++)
            {
                if (currentCapacity >= volumes[i])
                {
                    // 递归探寻放入当前物品的情况，下一层从下一个物品 i + 1 开始选择
                    Solve(currentCapacity - volumes[i], i + 1);
                }
            }
        }
    }
}
```
