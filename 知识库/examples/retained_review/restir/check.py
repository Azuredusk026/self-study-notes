"""正文统计量的确定性算例，不宣称时空渲染器无偏。"""
from math import isclose
K=2
m=min(100,20*K)
assert m==40
S_current=4*2*K
S_history=1*1*m
assert (S_current,S_history)==(16,40)
assert isclose((S_current+S_history)/((K+m)*1),4/3)
# 缩放流式S与M保持已归一化W。
assert isclose((100*(m/100))/m,100/100)
spatial_sum=56+4*2*2
assert isclose(spatial_sum/(44*4),9/22)
# 穷举当前代表a/b及最终选择，证明失配期望为1.5。
expectation=0
for current in ('a','b'):
 weights=(2,1)
 for weight in weights:
  probability=weight/sum(weights)
  estimate=sum(weights)/2
  expectation+=0.5*probability*estimate
assert isclose(expectation,1.5)
assert isclose(sum(0.5*2 for _ in ('a','b')),2)
assert .6 * (S_current+S_history) < S_history
assert not .8 * (S_current+S_history) < S_history
print('PASS: ReSTIR计数、归一化、空间合并和支持反例，9项断言')
