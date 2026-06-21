# 技术美术常用简单算法题整理

面向技术美术实习面试，重点覆盖几何计算、包围盒碰撞、插值、坐标变换、渲染辅助与工具脚本中常见的小算法。代码默认使用 C++17 风格，尽量保持简单、可直接手写。

---

## 目录

1. 点到直线距离
2. 点到线段距离
3. 判断点是否在三角形内
4. AABB 与 AABB 是否相交
5. AABB 与点是否相交
6. 圆与圆是否相交
7. 球与球是否相交
8. 线段与线段相交
9. 射线与平面相交
10. 射线与球相交
11. Clamp 限制数值范围
12. Lerp 线性插值
13. SmoothStep 平滑插值
14. Remap 数值区间映射
15. 向量归一化
16. 计算两向量夹角
17. 反射向量计算
18. 简单重心坐标
19. 多边形面积 Shoelace Formula
20. 2D 点绕中心旋转
21. 判断三角形朝向
22. 包围盒合并
23. 简单视锥体 AABB 裁剪思路
24. 颜色 Gamma / Linear 转换
25. HSV 转 RGB

---

## 公共基础代码

```cpp
#include <cmath>
#include <algorithm>
#include <vector>
#include <iostream>

const float EPS = 1e-6f;

struct Vec2 {
    float x, y;

    Vec2() : x(0), y(0) {}
    Vec2(float x_, float y_) : x(x_), y(y_) {}

    Vec2 operator+(const Vec2& other) const { return {x + other.x, y + other.y}; }
    Vec2 operator-(const Vec2& other) const { return {x - other.x, y - other.y}; }
    Vec2 operator*(float s) const { return {x * s, y * s}; }
};

struct Vec3 {
    float x, y, z;

    Vec3() : x(0), y(0), z(0) {}
    Vec3(float x_, float y_, float z_) : x(x_), y(y_), z(z_) {}

    Vec3 operator+(const Vec3& other) const { return {x + other.x, y + other.y, z + other.z}; }
    Vec3 operator-(const Vec3& other) const { return {x - other.x, y - other.y, z - other.z}; }
    Vec3 operator*(float s) const { return {x * s, y * s, z * s}; }
};

float Dot(const Vec2& a, const Vec2& b) {
    return a.x * b.x + a.y * b.y;
}

float Dot(const Vec3& a, const Vec3& b) {
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

float Cross2D(const Vec2& a, const Vec2& b) {
    return a.x * b.y - a.y * b.x;
}

Vec3 Cross(const Vec3& a, const Vec3& b) {
    return {
        a.y * b.z - a.z * b.y,
        a.z * b.x - a.x * b.z,
        a.x * b.y - a.y * b.x
    };
}

float Length(const Vec2& v) {
    return std::sqrt(Dot(v, v));
}

float Length(const Vec3& v) {
    return std::sqrt(Dot(v, v));
}
```

---

# 1. 点到直线距离

## 技术美术场景

用于判断鼠标点到一条边的距离、描边检测、曲线编辑器中点选线段附近区域等。

## 题目

给定点 `P`，以及直线上的两个点 `A`、`B`，求点 `P` 到直线 `AB` 的距离。

## 思路

二维中可以用叉积面积公式：

```text
距离 = |(B - A) x (P - A)| / |B - A|
```

## 代码

```cpp
float DistancePointToLine(const Vec2& p, const Vec2& a, const Vec2& b) {
    Vec2 ab = b - a;
    Vec2 ap = p - a;
    float area2 = std::abs(Cross2D(ab, ap));
    float base = Length(ab);

    if (base < EPS) {
        return Length(ap);
    }

    return area2 / base;
}
```

## 复杂度

时间复杂度：`O(1)`  
空间复杂度：`O(1)`

---

# 2. 点到线段距离

## 技术美术场景

用于曲线控制点选择、骨骼连线点击、2D 编辑器中选择最近边。

## 题目

给定点 `P` 和线段 `AB`，求 `P` 到线段 `AB` 的最短距离。

## 思路

先将点投影到直线 `AB` 上，得到参数 `t`：

```text
t = dot(P - A, B - A) / |B - A|^2
```

如果 `t < 0`，最近点是 `A`。  
如果 `t > 1`，最近点是 `B`。  
否则最近点在线段中间。

## 代码

```cpp
float DistancePointToSegment(const Vec2& p, const Vec2& a, const Vec2& b) {
    Vec2 ab = b - a;
    Vec2 ap = p - a;

    float abLenSq = Dot(ab, ab);
    if (abLenSq < EPS) {
        return Length(ap);
    }

    float t = Dot(ap, ab) / abLenSq;
    t = std::max(0.0f, std::min(1.0f, t));

    Vec2 closest = a + ab * t;
    return Length(p - closest);
}
```

## 复杂度

时间复杂度：`O(1)`  
空间复杂度：`O(1)`

---

# 3. 判断点是否在三角形内

## 技术美术场景

用于网格拾取、三角面点击检测、UV 三角形内部判断。

## 题目

给定二维点 `P` 和三角形 `ABC`，判断 `P` 是否在三角形内部。

## 思路

使用叉积判断点是否在三条边的同一侧。  
如果三次叉积符号一致，则点在三角形内。

## 代码

```cpp
bool PointInTriangle(const Vec2& p, const Vec2& a, const Vec2& b, const Vec2& c) {
    float c1 = Cross2D(b - a, p - a);
    float c2 = Cross2D(c - b, p - b);
    float c3 = Cross2D(a - c, p - c);

    bool hasNeg = (c1 < -EPS) || (c2 < -EPS) || (c3 < -EPS);
    bool hasPos = (c1 > EPS) || (c2 > EPS) || (c3 > EPS);

    return !(hasNeg && hasPos);
}
```

## 复杂度

时间复杂度：`O(1)`  
空间复杂度：`O(1)`

---

# 4. AABB 与 AABB 是否相交

## 技术美术场景

用于粗略碰撞检测、选择框检测、包围盒裁剪、粒子或特效区域判断。

## 题目

给定两个二维 AABB，判断它们是否相交。

## 思路

AABB 相交的条件：两个盒子在 X 轴和 Y 轴上都有重叠。

## 代码

```cpp
struct AABB2D {
    Vec2 min;
    Vec2 max;
};

bool IntersectAABB(const AABB2D& a, const AABB2D& b) {
    if (a.max.x < b.min.x || a.min.x > b.max.x) return false;
    if (a.max.y < b.min.y || a.min.y > b.max.y) return false;
    return true;
}
```

## 复杂度

时间复杂度：`O(1)`  
空间复杂度：`O(1)`

---

# 5. AABB 与点是否相交

## 技术美术场景

用于 UI 点击区域判断、框选工具、2D gizmo 选择。

## 题目

给定一个点 `P` 和一个 AABB，判断点是否在盒子内部。

## 代码

```cpp
bool PointInAABB(const Vec2& p, const AABB2D& box) {
    return p.x >= box.min.x && p.x <= box.max.x &&
           p.y >= box.min.y && p.y <= box.max.y;
}
```

## 复杂度

时间复杂度：`O(1)`  
空间复杂度：`O(1)`

---

# 6. 圆与圆是否相交

## 技术美术场景

用于 2D 特效范围判断、技能范围检测、屏幕空间圆形区域选择。

## 题目

给定两个圆的圆心和半径，判断两个圆是否相交。

## 思路

如果两个圆心之间的距离小于等于半径之和，则相交。为了避免开方，可以比较距离平方。

## 代码

```cpp
bool IntersectCircle(const Vec2& c1, float r1, const Vec2& c2, float r2) {
    Vec2 d = c1 - c2;
    float distSq = Dot(d, d);
    float radiusSum = r1 + r2;
    return distSq <= radiusSum * radiusSum;
}
```

## 复杂度

时间复杂度：`O(1)`  
空间复杂度：`O(1)`

---

# 7. 球与球是否相交

## 技术美术场景

用于 3D 特效范围、包围球粗略碰撞、LOD 距离判断。

## 题目

给定两个球体的球心和半径，判断是否相交。

## 代码

```cpp
bool IntersectSphere(const Vec3& c1, float r1, const Vec3& c2, float r2) {
    Vec3 d = c1 - c2;
    float distSq = Dot(d, d);
    float radiusSum = r1 + r2;
    return distSq <= radiusSum * radiusSum;
}
```

## 复杂度

时间复杂度：`O(1)`  
空间复杂度：`O(1)`

---

# 8. 线段与线段相交

## 技术美术场景

用于 2D 多边形编辑、笔刷路径交叉检测、UV 岛边界检测。

## 题目

给定二维线段 `AB` 和 `CD`，判断它们是否相交。

## 思路

使用方向测试。两条线段相交时，一般满足：

```text
A、B 在 CD 两侧，并且 C、D 在 AB 两侧
```

## 代码

```cpp
float Orientation(const Vec2& a, const Vec2& b, const Vec2& c) {
    return Cross2D(b - a, c - a);
}

bool OnSegment(const Vec2& p, const Vec2& a, const Vec2& b) {
    return p.x >= std::min(a.x, b.x) - EPS && p.x <= std::max(a.x, b.x) + EPS &&
           p.y >= std::min(a.y, b.y) - EPS && p.y <= std::max(a.y, b.y) + EPS;
}

bool SegmentIntersect(const Vec2& a, const Vec2& b, const Vec2& c, const Vec2& d) {
    float o1 = Orientation(a, b, c);
    float o2 = Orientation(a, b, d);
    float o3 = Orientation(c, d, a);
    float o4 = Orientation(c, d, b);

    if (o1 * o2 < -EPS && o3 * o4 < -EPS) {
        return true;
    }

    if (std::abs(o1) < EPS && OnSegment(c, a, b)) return true;
    if (std::abs(o2) < EPS && OnSegment(d, a, b)) return true;
    if (std::abs(o3) < EPS && OnSegment(a, c, d)) return true;
    if (std::abs(o4) < EPS && OnSegment(b, c, d)) return true;

    return false;
}
```

## 复杂度

时间复杂度：`O(1)`  
空间复杂度：`O(1)`

---

# 9. 射线与平面相交

## 技术美术场景

用于鼠标射线拾取地面、编辑器 gizmo 操作、点击场景放置物体。

## 题目

给定射线 `origin + t * dir`，以及平面上一点 `planePoint` 和法线 `planeNormal`，求射线是否击中平面。

## 思路

平面方程：

```text
dot(X - planePoint, normal) = 0
```

代入射线公式，求出 `t`。

## 代码

```cpp
bool RayPlaneIntersect(
    const Vec3& rayOrigin,
    const Vec3& rayDir,
    const Vec3& planePoint,
    const Vec3& planeNormal,
    float& outT
) {
    float denom = Dot(rayDir, planeNormal);

    if (std::abs(denom) < EPS) {
        return false;
    }

    outT = Dot(planePoint - rayOrigin, planeNormal) / denom;
    return outT >= 0.0f;
}
```

## 复杂度

时间复杂度：`O(1)`  
空间复杂度：`O(1)`

---

# 10. 射线与球相交

## 技术美术场景

用于 3D 点选、粗略碰撞、技能命中检测。

## 题目

给定射线和球体，判断射线是否击中球，并返回最近命中距离。

## 思路

将射线代入球方程：

```text
|origin + t * dir - center|^2 = r^2
```

得到一元二次方程。判别式小于 0 则不相交。

## 代码

```cpp
bool RaySphereIntersect(
    const Vec3& rayOrigin,
    const Vec3& rayDir,
    const Vec3& center,
    float radius,
    float& outT
) {
    Vec3 oc = rayOrigin - center;

    float a = Dot(rayDir, rayDir);
    float b = 2.0f * Dot(oc, rayDir);
    float c = Dot(oc, oc) - radius * radius;

    float discriminant = b * b - 4.0f * a * c;
    if (discriminant < 0.0f) {
        return false;
    }

    float sqrtD = std::sqrt(discriminant);
    float t1 = (-b - sqrtD) / (2.0f * a);
    float t2 = (-b + sqrtD) / (2.0f * a);

    if (t1 >= 0.0f) {
        outT = t1;
        return true;
    }

    if (t2 >= 0.0f) {
        outT = t2;
        return true;
    }

    return false;
}
```

## 复杂度

时间复杂度：`O(1)`  
空间复杂度：`O(1)`

---

# 11. Clamp 限制数值范围

## 技术美术场景

用于限制颜色、权重、动画参数、材质参数范围。

## 题目

实现一个函数，将数值限制在 `[minValue, maxValue]` 区间内。

## 代码

```cpp
float Clamp(float value, float minValue, float maxValue) {
    return std::max(minValue, std::min(value, maxValue));
}
```

## 复杂度

时间复杂度：`O(1)`  
空间复杂度：`O(1)`

---

# 12. Lerp 线性插值

## 技术美术场景

用于动画过渡、颜色渐变、材质参数混合、相机移动。

## 题目

实现线性插值：当 `t = 0` 返回 `a`，当 `t = 1` 返回 `b`。

## 代码

```cpp
float Lerp(float a, float b, float t) {
    return a + (b - a) * t;
}

Vec3 Lerp(const Vec3& a, const Vec3& b, float t) {
    return a + (b - a) * t;
}
```

## 复杂度

时间复杂度：`O(1)`  
空间复杂度：`O(1)`

---

# 13. SmoothStep 平滑插值

## 技术美术场景

用于软边遮罩、溶解边缘、渐变过渡、shader 中平滑阈值。

## 题目

实现 `SmoothStep(edge0, edge1, x)`。

## 思路

先将 `x` 映射到 `[0, 1]`，再使用：

```text
t * t * (3 - 2 * t)
```

## 代码

```cpp
float SmoothStep(float edge0, float edge1, float x) {
    float t = Clamp((x - edge0) / (edge1 - edge0), 0.0f, 1.0f);
    return t * t * (3.0f - 2.0f * t);
}
```

## 复杂度

时间复杂度：`O(1)`  
空间复杂度：`O(1)`

---

# 14. Remap 数值区间映射

## 技术美术场景

用于把距离映射到透明度、把高度映射到颜色、把灰度映射到特效强度。

## 题目

把 `value` 从 `[inMin, inMax]` 映射到 `[outMin, outMax]`。

## 代码

```cpp
float Remap(float value, float inMin, float inMax, float outMin, float outMax) {
    if (std::abs(inMax - inMin) < EPS) {
        return outMin;
    }

    float t = (value - inMin) / (inMax - inMin);
    return Lerp(outMin, outMax, t);
}
```

## 复杂度

时间复杂度：`O(1)`  
空间复杂度：`O(1)`

---

# 15. 向量归一化

## 技术美术场景

用于方向向量、法线、光照方向、速度方向。

## 题目

实现向量归一化。

## 代码

```cpp
Vec3 Normalize(const Vec3& v) {
    float len = Length(v);
    if (len < EPS) {
        return {0.0f, 0.0f, 0.0f};
    }
    return v * (1.0f / len);
}
```

## 复杂度

时间复杂度：`O(1)`  
空间复杂度：`O(1)`

---

# 16. 计算两向量夹角

## 技术美术场景

用于朝向判断、视野角检测、法线夹角、光照角度。

## 题目

给定两个向量，求它们之间的夹角，单位为弧度。

## 思路

```text
cos(theta) = dot(a, b) / (|a| * |b|)
```

注意 `acos` 输入要限制在 `[-1, 1]`。

## 代码

```cpp
float AngleBetween(const Vec3& a, const Vec3& b) {
    float lenA = Length(a);
    float lenB = Length(b);

    if (lenA < EPS || lenB < EPS) {
        return 0.0f;
    }

    float cosTheta = Dot(a, b) / (lenA * lenB);
    cosTheta = Clamp(cosTheta, -1.0f, 1.0f);
    return std::acos(cosTheta);
}
```

## 复杂度

时间复杂度：`O(1)`  
空间复杂度：`O(1)`

---

# 17. 反射向量计算

## 技术美术场景

用于反射光照、镜面方向、弹射方向、shader 中 `reflect` 的原理。

## 题目

给定入射方向 `I` 和法线 `N`，计算反射方向。

## 思路

```text
R = I - 2 * dot(I, N) * N
```

要求 `N` 最好是单位向量。

## 代码

```cpp
Vec3 Reflect(const Vec3& incident, const Vec3& normal) {
    return incident - normal * (2.0f * Dot(incident, normal));
}
```

## 复杂度

时间复杂度：`O(1)`  
空间复杂度：`O(1)`

---

# 18. 简单重心坐标

## 技术美术场景

用于三角形内插、UV 插值、顶点颜色插值、软选择权重。

## 题目

给定三角形 `ABC` 和点 `P`，计算 `P` 的重心坐标。

## 思路

重心坐标可表示为：

```text
P = u * A + v * B + w * C
u + v + w = 1
```

## 代码

```cpp
Vec3 Barycentric(const Vec2& p, const Vec2& a, const Vec2& b, const Vec2& c) {
    Vec2 v0 = b - a;
    Vec2 v1 = c - a;
    Vec2 v2 = p - a;

    float d00 = Dot(v0, v0);
    float d01 = Dot(v0, v1);
    float d11 = Dot(v1, v1);
    float d20 = Dot(v2, v0);
    float d21 = Dot(v2, v1);

    float denom = d00 * d11 - d01 * d01;
    if (std::abs(denom) < EPS) {
        return {-1.0f, -1.0f, -1.0f};
    }

    float v = (d11 * d20 - d01 * d21) / denom;
    float w = (d00 * d21 - d01 * d20) / denom;
    float u = 1.0f - v - w;

    return {u, v, w};
}
```

## 复杂度

时间复杂度：`O(1)`  
空间复杂度：`O(1)`

---

# 19. 多边形面积 Shoelace Formula

## 技术美术场景

用于 2D 多边形工具、UV 岛面积计算、轮廓面积估计。

## 题目

给定一个按顺序排列的二维多边形顶点数组，求多边形面积。

## 代码

```cpp
float PolygonArea(const std::vector<Vec2>& points) {
    int n = static_cast<int>(points.size());
    if (n < 3) return 0.0f;

    float sum = 0.0f;
    for (int i = 0; i < n; ++i) {
        const Vec2& a = points[i];
        const Vec2& b = points[(i + 1) % n];
        sum += a.x * b.y - a.y * b.x;
    }

    return std::abs(sum) * 0.5f;
}
```

## 复杂度

时间复杂度：`O(n)`  
空间复杂度：`O(1)`

---

# 20. 2D 点绕中心旋转

## 技术美术场景

用于 UI 元素旋转、2D 特效轨迹、编辑器中旋转点集。

## 题目

给定点 `P`、旋转中心 `C` 和角度 `angleRad`，求旋转后的点。

## 代码

```cpp
Vec2 RotatePoint(const Vec2& p, const Vec2& center, float angleRad) {
    float s = std::sin(angleRad);
    float c = std::cos(angleRad);

    Vec2 local = p - center;

    Vec2 rotated;
    rotated.x = local.x * c - local.y * s;
    rotated.y = local.x * s + local.y * c;

    return center + rotated;
}
```

## 复杂度

时间复杂度：`O(1)`  
空间复杂度：`O(1)`

---

# 21. 判断三角形朝向

## 技术美术场景

用于判断三角形顶点顺序、背面剔除、网格法线问题排查。

## 题目

给定二维三角形 `ABC`，判断它是顺时针还是逆时针。

## 思路

计算叉积：

```text
cross(B - A, C - A)
```

大于 0 通常表示逆时针，小于 0 表示顺时针。

## 代码

```cpp
int TriangleOrientation(const Vec2& a, const Vec2& b, const Vec2& c) {
    float cross = Cross2D(b - a, c - a);

    if (cross > EPS) return 1;   // Counter-clockwise
    if (cross < -EPS) return -1; // Clockwise
    return 0;                    // Degenerate
}
```

## 复杂度

时间复杂度：`O(1)`  
空间复杂度：`O(1)`

---

# 22. 包围盒合并

## 技术美术场景

用于计算模型整体包围盒、合并多个子网格的 Bounds、场景区域划分。

## 题目

给定两个 AABB，返回能同时包住它们的新 AABB。

## 代码

```cpp
AABB2D UnionAABB(const AABB2D& a, const AABB2D& b) {
    AABB2D result;
    result.min.x = std::min(a.min.x, b.min.x);
    result.min.y = std::min(a.min.y, b.min.y);
    result.max.x = std::max(a.max.x, b.max.x);
    result.max.y = std::max(a.max.y, b.max.y);
    return result;
}
```

## 复杂度

时间复杂度：`O(1)`  
空间复杂度：`O(1)`

---

# 23. 简单视锥体 AABB 裁剪思路

## 技术美术场景

用于粗略剔除不可见物体、编辑器视口优化、特效对象可见性判断。

## 题目

给定一个 AABB 和视锥体的 6 个平面，判断 AABB 是否可能在视锥体内。

## 思路

对每个平面，找到 AABB 在该平面法线方向上最远的点。  
如果这个点仍然在平面外，则整个 AABB 被剔除。

## 代码

```cpp
struct Plane {
    Vec3 normal;
    float d;
};

struct AABB3D {
    Vec3 min;
    Vec3 max;
};

float PlaneDistance(const Plane& plane, const Vec3& p) {
    return Dot(plane.normal, p) + plane.d;
}

bool AABBInFrustum(const AABB3D& box, const std::vector<Plane>& planes) {
    for (const Plane& plane : planes) {
        Vec3 positive;
        positive.x = (plane.normal.x >= 0.0f) ? box.max.x : box.min.x;
        positive.y = (plane.normal.y >= 0.0f) ? box.max.y : box.min.y;
        positive.z = (plane.normal.z >= 0.0f) ? box.max.z : box.min.z;

        if (PlaneDistance(plane, positive) < 0.0f) {
            return false;
        }
    }

    return true;
}
```

## 复杂度

时间复杂度：`O(6)`，实际可视为 `O(1)`  
空间复杂度：`O(1)`

---

# 24. 颜色 Gamma / Linear 转换

## 技术美术场景

用于解释 Unity / Unreal 中 Linear Space 与 Gamma Space，调试颜色偏差。

## 题目

实现单通道颜色的 Gamma 与 Linear 近似转换。

## 代码

```cpp
float GammaToLinear(float gammaValue) {
    return std::pow(gammaValue, 2.2f);
}

float LinearToGamma(float linearValue) {
    return std::pow(linearValue, 1.0f / 2.2f);
}
```

## 复杂度

时间复杂度：`O(1)`  
空间复杂度：`O(1)`

---

# 25. HSV 转 RGB

## 技术美术场景

用于颜色选择器、渐变工具、材质颜色程序化生成。

## 题目

给定 HSV 颜色，范围均为 `[0, 1]`，转换为 RGB。

## 代码

```cpp
Vec3 HSVToRGB(float h, float s, float v) {
    h = h - std::floor(h);
    s = Clamp(s, 0.0f, 1.0f);
    v = Clamp(v, 0.0f, 1.0f);

    float c = v * s;
    float x = c * (1.0f - std::abs(std::fmod(h * 6.0f, 2.0f) - 1.0f));
    float m = v - c;

    Vec3 rgb;
    float hp = h * 6.0f;

    if (hp < 1.0f) {
        rgb = {c, x, 0.0f};
    } else if (hp < 2.0f) {
        rgb = {x, c, 0.0f};
    } else if (hp < 3.0f) {
        rgb = {0.0f, c, x};
    } else if (hp < 4.0f) {
        rgb = {0.0f, x, c};
    } else if (hp < 5.0f) {
        rgb = {x, 0.0f, c};
    } else {
        rgb = {c, 0.0f, x};
    }

    return {rgb.x + m, rgb.y + m, rgb.z + m};
}
```

## 复杂度

时间复杂度：`O(1)`  
空间复杂度：`O(1)`

---

## 常见追问

### 1. 为什么距离判断常用平方距离？

因为开方 `sqrt` 相对更贵。如果只是比较距离大小，可以比较平方距离。

```cpp
bool IsWithinRange(const Vec3& a, const Vec3& b, float range) {
    Vec3 d = a - b;
    return Dot(d, d) <= range * range;
}
```

### 2. 为什么要使用 EPS？

浮点数计算存在误差，不能直接用 `== 0` 判断。  
更稳妥的写法是：

```cpp
if (std::abs(value) < EPS) {
    // Treat as zero
}
```

### 3. 点积和叉积分别常用来做什么？

点积常用于：

- 判断夹角
- 判断方向是否相近
- 投影长度
- 光照中的 Lambert 漫反射

叉积常用于：

- 判断左右侧
- 计算面积
- 求法线
- 判断三角形顶点顺序

---

