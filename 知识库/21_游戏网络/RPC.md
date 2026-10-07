# RPC

服务端执行了请求，响应却丢了，客户端无法由超时判断是否成功。RPC需要请求ID、权限和幂等边界，重试查询已有结果，避免一次加金币变成两次。

## RPC

RPC 由 IDL/Schema 描述可调用消息，生成或手写 Stub 负责序列化、发送和分发。网络 RPC 不具有本地调用的可靠语义：它可能延迟、超时、重复执行，也可能在响应回来前连接断开。

每个请求应有 Request ID、权限上下文和超时。自动重试只适合幂等操作，或服务端用唯一事务号去重。`SetName(A)` 可以设计成幂等，`AddGold(100)` 若重复执行就会出错。关键交易最好表达为“提交事务 X”，并保存处理结果。

客户端 RPC 只是请求，服务端必须重新验证位置、冷却、资源和身份。函数名叫 `ServerDealDamage` 并不会让传入伤害可信。

HTTP/HTTPS 适合登录、配置、商城和内容清单等控制面请求；高频状态同步通常使用长连接或数据报形成实时数据面。两类流量可以采用不同的超时、重试、扩缩容和观测策略。

TLS 在传输之上提供身份认证、机密性和完整性。客户端验证证书链与域名，握手协商密钥和算法，之后使用对称加密传输。TLS 不能替代应用权限检查，也不能防止已经取得合法会话的客户端发送作弊请求。

Mirror 等引擎网络库把 RPC、对象生成和 SyncVar 封装为组件接口。SyncVar 只负责同步声明的数据变化，不会自动解决所有权、预测、权限和带宽预算。使用框架时仍要查看实际发送频率、序列化字节和服务端验证路径。

## 安全边界

握手阶段验证版本与身份，传输层按需要使用成熟的加密和认证协议。不要自创密码学。解析器限制包大小、频率和嵌套深度，网关按连接与账号做 Rate Limit。错误日志避免回显令牌和敏感载荷。

UDP 需要额外防止地址伪造与放大攻击。建立会话前不要对小请求返回巨大数据，关键消息带会话验证信息。断线重连时旧连接和重放包也必须失效。

## 幂等请求

模型伪代码由服务端以账号与事务ID共同去重，结果记录与状态变化位于一致的事务边界。

```text
validate session, schema and permission
if transaction already committed: return stored result
begin transaction
apply validated state change
store result under transactionId
commit
```

## 验证方法

在执行前后和响应前注入断线，重试应返回同一结果。测试权限、版本、非法长度及重复事务；TLS保护传输，不替代业务验证。

实现状态：正文代码是机制片段或明确标注的伪代码，完整类型、资源与调用宿主按所述环境补齐。实际CPU与编译检查见对应实验链接；目标引擎运行与GPU测量为UNVERIFIED。

## 相关主题

- [[21_游戏网络/对局服务器架构]]
- [[21_游戏网络/游戏网络传输]]
- [[21_游戏网络/游戏网络时钟]]

## 参考资料

- Glenn Fiedler, *Networking for Game Programmers*.
- IETF TCP, UDP and QUIC RFCs.
- Valve, *Source Multiplayer Networking*.
- Cloudflare Learning Center and IETF DNS RFCs.
