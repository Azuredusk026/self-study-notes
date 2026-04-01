# 第三章详细复习：积分学

## 1. 积分的两张面孔
*   **不定积分 (Indefinite Integral)：** 求导的逆过程，结果一定要加常数 **$+ C$**。
*   **定积分 (Definite Integral)：** 计算曲线下的面积，结果是一个具体的 **数值**。
*   **微积分基本定理 (FTC)：** 连接两者的桥梁。$\int_a^b f(x)dx = F(b) - F(a)$。

## 2. 积分计算四大绝招 - **期末必杀技**
1.  **直接积分：** 熟记基本公式（导数公式倒过来背，如 $\int \sec^2 x dx = \tan x + C$）。
2.  **代换法 (u-Substitution)：** 
    *   **核心逻辑：** 找函数里的一块设为 $u$，使它的导数也在函数里。
    *   **例子：** $\int 2x e^{x^2} dx$，设 $u = x^2$，则 $du = 2x dx$。
3.  **分部积分 (Integration by Parts)：** $\int u dv = uv - \int v du$。
    *   **口诀：** 选 $u$ 的顺序按 **LIATE** (Log, Inverse Trig, Algebraic, Trig, Exponential)。
4.  **三角代换 (Trig Sub)：** 专门对付根号下的平方。
    *   看到 $\sqrt{a^2-x^2}$：设 $x = a\sin\theta$。
    *   看到 $\sqrt{a^2+x^2}$：设 $x = a\tan\theta$。

## 3. 几何应用 - **大题常客**
*   **求面积 (Area)：** $\int_{left}^{right} (\text{上曲线} - \text{下曲线}) dx$。
*   **求体积 (Volume)：**
    *   **圆盘/垫片法 (Disk/Washer)：** $V = \int \pi (R_{out}^2 - r_{in}^2) dx$。
    *   **壳法 (Shell Method)：** $V = \int 2\pi (\text{半径}) (\text{高}) dx$。
*   **弧长 (Arc Length)：** $L = \int \sqrt{1 + [f'(x)]^2} dx$。

## 4. 反常积分 (Improper Integrals)
看到积分限有 $\infty$ 或者函数在某点会变成 $\infty$：
*   先写成极限形式：$\lim_{t \to \infty} \int_a^t f(x)dx$。
*   如果算出来是数，叫 **收敛 (Convergent)**；如果是 $\infty$ 或不存在，叫 **发散 (Divergent)**。

---
**本章解题锦囊：**
*   **死穴：** 漏掉 $+C$。不定积分不加 $C$ 会被扣分扣到哭。
*   **换元法一定要换限：** 算定积分用 $u$ 代换后，上下限也要跟着变成 $u$ 的值。
*   遇到 $\frac{1}{x^2+a^2}$ 的积分，直接想 $\arctan$。
