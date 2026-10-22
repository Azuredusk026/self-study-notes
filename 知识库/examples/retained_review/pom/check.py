"""正文的独立标量算例；不模拟纹理硬件。"""
from math import isclose
assert isclose(0.6-0.2*0.6, 0.48)
t=0.6/1.2
assert isclose(t,0.5) and isclose(0.6-0.2*t,t)
w=0.1/(0.1-(-0.15))
assert isclose(w,0.4)
assert isclose((1-w)*0.1+w*(-0.15),0)
assert isclose(0.6-0.2*0.3,0.54)
assert 0.6-0.2 > 0.3+0.01
assert not 0.6-0.2 > 0.5+0.01
# 两端都在空气中并不能排除区间内的薄凸起。
D=lambda q: 0.1 if 0.29 < q < 0.31 else 0.8
assert all(0.6-q <= D(q)+0.01 for q in (0.2,0.4))
assert 0.6-0.3 > D(0.3)+0.01
print('PASS: POM交点、插值、自阴影和漏检反例，9项断言')
