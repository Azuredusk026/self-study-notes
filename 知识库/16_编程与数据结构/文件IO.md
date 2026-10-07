# 文件IO

第一次读慢、第二次读快，可能只是命中系统页缓存。文件IO先区分冷暖缓存与顺序随机访问，异步请求再安排完成与缓冲寿命。写临时文件再替换目标时，原子可见和持久化也有不同保证。

## 文件系统与 IO

文件系统按路径解析目录项，再通过文件元数据定位数据块。Page Cache 会缓存最近读写的数据，因此一次读很快可能只是命中缓存。性能测试要区分冷缓存、热缓存、顺序读、随机读和存储设备队列深度。

Buffered IO 经过系统缓存，Direct IO 绕过部分缓存并要求更严格的对齐和块大小。Asynchronous IO 让线程提交请求后继续工作，完成事件由系统通知；它适合资产流送，但仍需要请求合并、优先级、取消和目标 Buffer 生命周期管理。

原子替换常先写临时文件、Flush 并关闭，再 Rename/Replace 正式路径。`Flush` 的语义受系统和设备缓存影响，需要持久化保证时应使用平台明确提供的同步接口。

## 临时文件发布

伪代码要求临时文件与目标位于支持原子替换的同一文件系统，持久化保证按平台接口实现。

```text
write temporary file
flush according to durability requirement
close and validate content
replace destination atomically where supported
sync containing metadata if required by platform
```

## 验证方法

分别测冷暖缓存、顺序随机与限速设备。故障注入到写入、flush和replace边界，检查正式版本仍是完整旧版或新版。取消异步IO后缓冲活到请求实际完成。

实现状态：正文代码是机制片段或明确标注的伪代码，完整类型、资源与调用宿主按所述环境补齐。实际CPU与编译检查见对应实验链接；目标引擎运行与GPU测量为UNVERIFIED。

## 相关主题

- [[15_资产与工具管线/资产构建与发布]]
- [[16_编程与数据结构/虚拟内存]]
- [[16_编程与数据结构/进程与调度]]
- [[16_编程与数据结构/线程同步]]

## 参考资料

- Silberschatz et al., *Operating System Concepts*.
- Tanenbaum and Bos, *Modern Operating Systems*.
- C++ Reference, *Memory model* and *Atomic operations*.
- Microsoft Learn, Windows processes, threads, virtual memory and asynchronous I/O.
