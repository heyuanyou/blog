---
title: "Redis"
date: 2025-12-26
main: "面试"
sub: ["redis", "nosql"]
summary: "Redis介绍，涵盖基础到高级的各个方面，包括数据结构、持久化、高可用、性能优化等"
---

# Redis 面试题

## 目录

- [基础概念](#基础概念)
- [数据结构详解](#数据结构详解)
- [持久化机制](#持久化机制)
- [主从复制](#主从复制)
- [哨兵模式](#哨兵模式)
- [集群模式](#集群模式)
- [性能优化](#性能优化)
- [缓存策略](#缓存策略)
- [事务与管道](#事务与管道)
- [常见问题与解决方案](#常见问题与解决方案)
- [高级特性](#高级特性)

---

## 基础概念

### 1. 什么是 Redis？它有哪些特点？

**答案：**
Redis（Remote Dictionary Server）是一个开源的、基于内存的数据结构存储系统，可以用作数据库、缓存和消息中间件。

**主要特点：**
- **高性能**：基于内存操作，读写速度极快（10万+ QPS）
- **丰富的数据类型**：支持 String、Hash、List、Set、Sorted Set、Stream 等
- **持久化**：支持 RDB 和 AOF 两种持久化方式
- **高可用**：支持主从复制、哨兵模式、集群模式
- **原子操作**：所有操作都是原子性的
- **发布订阅**：支持消息的发布订阅模式
- **事务支持**：支持事务，保证命令的原子性执行

### 2. Redis 为什么这么快？

**答案：**

**1. 基于内存存储**
- 数据存储在内存中，避免了磁盘 I/O 的开销
- 内存访问速度比磁盘快几个数量级

**2. 单线程模型（6.0 之前）**
- 避免了线程切换和锁竞争的开销
- 单线程避免了上下文切换，CPU 利用率高
- 6.0+ 版本引入了多线程 I/O，但命令执行仍是单线程

**3. 高效的数据结构**
- 使用哈希表、跳表等高效数据结构
- 针对不同场景优化了底层实现

**4. 优化的网络模型**
- 使用 I/O 多路复用（epoll/kqueue）
- 非阻塞 I/O，避免等待

**5. C 语言实现**
- 底层用 C 语言实现，执行效率高

### 3. Redis 的数据类型有哪些？

**答案：**
Redis 支持以下数据类型：

| 类型 | 说明 | 应用场景 |
|------|------|---------|
| **String** | 字符串，最大 512MB | 缓存、计数器、分布式锁 |
| **Hash** | 键值对集合 | 存储对象、用户信息 |
| **List** | 双向链表 | 消息队列、最新列表 |
| **Set** | 无序集合 | 标签、去重、交集并集 |
| **Sorted Set** | 有序集合 | 排行榜、范围查询 |
| **Stream** | 消息流 | 消息队列、日志流 |
| **Bitmap** | 位图 | 布隆过滤器、统计 |
| **HyperLogLog** | 基数统计 | UV 统计 |
| **Geospatial** | 地理位置 | 附近的人、距离计算 |

### 4. Redis 的内存淘汰策略有哪些？

**答案：**
当内存达到上限时，Redis 会根据配置的策略淘汰数据：

**1. noeviction（默认）**
- 不淘汰，写入操作返回错误

**2. allkeys-lru**
- 从所有键中淘汰最近最少使用的（LRU）

**3. allkeys-lfu**
- 从所有键中淘汰最不经常使用的（LFU）

**4. allkeys-random**
- 从所有键中随机淘汰

**5. volatile-lru**
- 从设置了过期时间的键中淘汰最近最少使用的

**6. volatile-lfu**
- 从设置了过期时间的键中淘汰最不经常使用的

**7. volatile-random**
- 从设置了过期时间的键中随机淘汰

**8. volatile-ttl**
- 从设置了过期时间的键中淘汰即将过期的

**配置方式：**
```bash
# redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
```

### 5. Redis 的过期键删除策略？

**答案：**
Redis 使用两种策略删除过期键：

**1. 惰性删除（Lazy Expiration）**
- 访问键时检查是否过期，过期则删除
- 优点：对 CPU 友好，只处理访问的键
- 缺点：可能占用内存，过期键不被访问就不会删除

**2. 定期删除（Periodic Expiration）**
- 每隔一段时间扫描一定数量的过期键并删除
- 默认每秒执行 10 次，每次随机抽取 20 个键检查
- 优点：平衡内存和 CPU
- 缺点：可能删除不及时

**3. 内存淘汰策略配合**
- 当内存不足时，结合内存淘汰策略删除键

**配置：**
```bash
# redis.conf
# 每秒执行 10 次过期键扫描
hz 10
```

---

## 数据结构详解

### 6. String 类型的底层实现是什么？

**答案：**
String 类型底层使用 **SDS（Simple Dynamic String）** 实现。

**SDS 结构：**
```c
struct sdshdr {
    int len;        // 字符串长度
    int free;       // 剩余空间
    char buf[];     // 字符数组
};
```

**优势：**
1. **O(1) 获取长度**：直接读取 len 字段
2. **二进制安全**：可以存储任意二进制数据
3. **减少内存重分配**：预分配空间，减少内存分配次数
4. **兼容 C 字符串**：末尾有 '\0'，可以使用 C 字符串函数

**编码方式：**
- **int**：整数，直接存储
- **embstr**：小于 44 字节，嵌入式字符串
- **raw**：大于 44 字节，独立分配内存

### 7. Hash 类型的底层实现是什么？

**答案：**
Hash 类型底层使用**哈希表（Hash Table）**或**压缩列表（Ziplist）**实现。

**编码转换：**
- **Ziplist**：当 Hash 元素数量 < 512 且所有值 < 64 字节
- **Hashtable**：不满足 Ziplist 条件时使用

**Ziplist 结构：**
- 连续内存，节省空间
- 适合小数据量

**Hashtable 结构：**
- 使用字典（dict）实现
- 支持渐进式 rehash
- 适合大数据量

**渐进式 rehash：**
1. 同时维护两个哈希表（ht[0] 和 ht[1]）
2. 逐步将数据从 ht[0] 迁移到 ht[1]
3. 每次操作时迁移一部分
4. 迁移完成后，ht[1] 成为新的 ht[0]

### 8. List 类型的底层实现是什么？

**答案：**
List 类型底层使用**压缩列表（Ziplist）**或**双向链表（LinkedList）**实现。

**编码转换：**
- **Ziplist**：元素数量 < 512 且所有元素 < 64 字节
- **LinkedList**：不满足条件时使用

**3.2+ 版本使用 QuickList：**
- QuickList = 多个 Ziplist + 双向链表
- 结合了 Ziplist 的空间效率和 LinkedList 的灵活性

**操作复杂度：**
- **LPUSH/RPUSH**：O(1)
- **LPOP/RPOP**：O(1)
- **LINDEX**：O(N)
- **LRANGE**：O(S+N)，S 为起始位置，N 为元素数量

### 9. Set 类型的底层实现是什么？

**答案：**
Set 类型底层使用**整数集合（IntSet）**或**哈希表（Hashtable）**实现。

**编码转换：**
- **IntSet**：所有元素都是整数且数量 < 512
- **Hashtable**：不满足条件时使用（值存储为 NULL，只存储键）

**IntSet 结构：**
- 有序数组存储整数
- 根据最大元素决定编码（int16/int32/int64）
- 插入时可能需要升级编码

**操作复杂度：**
- **SADD**：O(1)
- **SMEMBERS**：O(N)
- **SISMEMBER**：O(1)
- **SINTER/SUNION**：O(N*M)

### 10. Sorted Set 类型的底层实现是什么？

**答案：**
Sorted Set 类型底层使用**压缩列表（Ziplist）**或**跳表（SkipList）+ 哈希表**实现。

**编码转换：**
- **Ziplist**：元素数量 < 128 且所有元素 < 64 字节
- **SkipList + Hashtable**：不满足条件时使用

**SkipList 结构：**
- 多层有序链表
- 上层节点数约为下层的一半
- 查找、插入、删除都是 O(log N)

**为什么使用 SkipList？**
- 支持范围查询
- 实现相对简单
- 性能稳定，最坏情况也是 O(log N)

**操作复杂度：**
- **ZADD**：O(log N)
- **ZRANGE**：O(log N + M)，M 为返回元素数
- **ZRANK**：O(log N)
- **ZSCORE**：O(1)（通过哈希表）

### 11. Stream 类型是什么？如何使用？

**答案：**
Stream 是 Redis 5.0 引入的新数据类型，用于消息流处理。

**核心概念：**
- **消息 ID**：唯一标识消息，格式为 `时间戳-序号`
- **消费者组**：多个消费者协同消费
- **ACK**：确认消息已处理

**基本操作：**
```bash
# 添加消息
XADD mystream * field1 value1 field2 value2

# 读取消息
XREAD COUNT 10 STREAMS mystream 0

# 创建消费者组
XGROUP CREATE mystream mygroup 0

# 消费者组读取
XREADGROUP GROUP mygroup consumer1 COUNT 1 STREAMS mystream >
```

**应用场景：**
- 消息队列
- 日志流
- 事件流处理

---

## 持久化机制

### 12. RDB 持久化是什么？优缺点？

**答案：**
RDB（Redis Database）是 Redis 的快照持久化方式。

**工作原理：**
- 在指定时间间隔内生成数据快照
- 将内存数据保存到磁盘的 RDB 文件
- 文件是二进制格式，体积小

**触发方式：**
1. **自动触发**：满足配置的 save 条件
2. **手动触发**：`SAVE`（阻塞）或 `BGSAVE`（后台）

**配置：**
```bash
# redis.conf
save 900 1      # 900秒内至少1个key变化
save 300 10     # 300秒内至少10个key变化
save 60 10000   # 60秒内至少10000个key变化
```

**优点：**
- 文件小，恢复快
- 适合备份和灾难恢复
- 对性能影响小（BGSAVE）

**缺点：**
- 可能丢失最后一次快照后的数据
- 数据量大时，fork 子进程可能阻塞
- 不适合实时持久化

### 13. AOF 持久化是什么？优缺点？

**答案：**
AOF（Append Only File）是 Redis 的日志持久化方式。

**工作原理：**
- 记录每个写操作命令
- 追加到 AOF 文件末尾
- 重启时重放 AOF 文件恢复数据

**同步策略：**
```bash
# redis.conf
appendfsync always      # 每个命令都同步（最安全，最慢）
appendfsync everysec    # 每秒同步一次（推荐）
appendfsync no          # 由操作系统决定（最快，可能丢数据）
```

**AOF 重写：**
- 定期重写 AOF 文件，去除冗余命令
- `BGREWRITEAOF` 手动触发
- 自动触发条件：`auto-aof-rewrite-percentage` 和 `auto-aof-rewrite-min-size`

**优点：**
- 数据丢失少（everysec 最多丢1秒）
- 可读性强，便于分析
- 支持误操作恢复（删除最后一条命令）

**缺点：**
- 文件体积大
- 恢复速度慢
- 对性能有一定影响

### 14. RDB 和 AOF 如何选择？

**答案：**

**使用场景对比：**

| 特性 | RDB | AOF |
|------|-----|-----|
| 文件大小 | 小 | 大 |
| 恢复速度 | 快 | 慢 |
| 数据丢失 | 可能丢失较多 | 丢失少 |
| 性能影响 | 小 | 中等 |
| 可读性 | 二进制 | 文本 |

**推荐配置：**
```bash
# 同时开启 RDB 和 AOF
save 900 1
appendonly yes
appendfsync everysec

# 优先使用 AOF 恢复（数据更完整）
aof-load-truncated yes
```

**最佳实践：**
- **数据安全要求高**：AOF everysec + RDB
- **性能要求高**：RDB
- **两者结合**：RDB 做备份，AOF 保证数据完整性

---

## 主从复制

### 15. Redis 主从复制原理是什么？

**答案：**
主从复制是 Redis 高可用的基础，一个主节点可以有多个从节点。

**复制流程：**

**1. 建立连接**
- 从节点执行 `SLAVEOF` 命令
- 从节点向主节点发送 `PING` 检查连接
- 主节点返回 `PONG`

**2. 身份验证**
- 如果配置了密码，从节点发送 `AUTH` 命令

**3. 同步数据**
- **全量复制**：
  1. 从节点发送 `PSYNC ? -1` 请求全量复制
  2. 主节点执行 `BGSAVE` 生成 RDB
  3. 主节点将 RDB 发送给从节点
  4. 从节点加载 RDB
  5. 主节点发送缓冲区中的写命令
- **增量复制**：
  1. 从节点发送 `PSYNC <runid> <offset>`
  2. 主节点判断 offset 是否在复制积压缓冲区
  3. 如果在，发送 offset 之后的命令
  4. 如果不在，执行全量复制

**4. 命令传播**
- 主节点执行写命令后，异步发送给从节点

**配置：**
```bash
# 从节点配置
replicaof <masterip> <masterport>
masterauth <password>
```

### 16. 主从复制的优缺点？

**答案：**

**优点：**
- **读写分离**：主节点写，从节点读，提高性能
- **数据备份**：从节点是主节点的备份
- **高可用**：主节点故障时，可以手动切换从节点
- **负载均衡**：多个从节点分担读压力

**缺点：**
- **数据延迟**：主从复制是异步的，可能有延迟
- **主节点压力**：多个从节点时，主节点压力大
- **故障切换**：需要手动切换，不能自动故障转移

### 17. 什么是复制积压缓冲区？

**答案：**
复制积压缓冲区（Replication Backlog）是主节点维护的一个固定大小的环形缓冲区。

**作用：**
- 存储最近执行的写命令
- 支持增量复制
- 避免频繁全量复制

**工作原理：**
1. 主节点执行写命令时，同时写入复制积压缓冲区
2. 从节点断线重连后，发送 offset
3. 如果 offset 在缓冲区内，主节点发送 offset 之后的命令
4. 如果 offset 不在缓冲区，执行全量复制

**配置：**
```bash
# redis.conf
repl-backlog-size 1mb      # 缓冲区大小
repl-backlog-ttl 3600      # 缓冲区保留时间（秒）
```

---

## 哨兵模式

### 18. Redis 哨兵（Sentinel）是什么？

**答案：**
哨兵是 Redis 的高可用解决方案，用于监控主从节点并自动故障转移。

**功能：**
1. **监控**：监控主从节点是否正常运行
2. **通知**：节点故障时通知管理员
3. **自动故障转移**：主节点故障时，自动选举新的主节点
4. **配置提供者**：客户端连接时，返回当前主节点地址

**架构：**
```
主节点 (Master)
  ├─ 从节点1 (Slave)
  └─ 从节点2 (Slave)

哨兵1 (Sentinel)
哨兵2 (Sentinel)
哨兵3 (Sentinel)  # 至少3个，保证选举
```

**配置：**
```bash
# sentinel.conf
sentinel monitor mymaster 127.0.0.1 6379 2
# 监控名为 mymaster 的主节点
# 127.0.0.1:6379 是主节点地址
# 2 表示至少2个哨兵认为主节点故障才进行故障转移

sentinel down-after-milliseconds mymaster 5000
# 5秒无响应认为节点故障

sentinel failover-timeout mymaster 10000
# 故障转移超时时间
```

### 19. 哨兵如何实现故障转移？

**答案：**

**故障转移流程：**

**1. 主观下线（SDOWN）**
- 单个哨兵认为主节点不可用
- 发送 `SENTINEL is-master-down-by-addr` 询问其他哨兵

**2. 客观下线（ODOWN）**
- 超过 `quorum` 数量的哨兵认为主节点不可用
- 进入故障转移流程

**3. 选举 Leader**
- 使用 Raft 算法选举 Leader 哨兵
- Leader 负责执行故障转移

**4. 选择新主节点**
- 过滤掉不健康的从节点
- 选择优先级最高的从节点
- 如果优先级相同，选择复制偏移量最大的
- 如果还相同，选择 runid 最小的

**5. 故障转移**
- Leader 哨兵执行 `SLAVEOF NO ONE` 提升从节点为主节点
- 向其他从节点发送 `SLAVEOF` 命令，指向新主节点
- 更新配置，通知客户端

**6. 原主节点恢复**
- 原主节点恢复后，成为新主节点的从节点

### 20. 哨兵模式的优缺点？

**答案：**

**优点：**
- **自动故障转移**：无需人工干预
- **高可用**：主节点故障自动切换
- **监控**：实时监控节点状态
- **配置管理**：统一管理主从配置

**缺点：**
- **数据丢失**：主从切换可能丢失数据
- **配置复杂**：需要配置多个哨兵
- **性能开销**：哨兵本身消耗资源
- **脑裂问题**：网络分区时可能出现多个主节点

---

## 集群模式

### 21. Redis 集群（Cluster）是什么？

**答案：**
Redis Cluster 是 Redis 的分布式解决方案，通过分片（Sharding）实现数据分布。

**核心概念：**
- **节点**：集群中的每个 Redis 实例
- **槽（Slot）**：16384 个槽，每个键映射到一个槽
- **分片**：每个节点负责一部分槽
- **Gossip 协议**：节点间通信协议

**架构：**
```
节点1: 槽 0-5460
节点2: 槽 5461-10922
节点3: 槽 10923-16383
```

**数据分布：**
- 使用 CRC16 算法计算 key 的哈希值
- `slot = CRC16(key) % 16384`
- 每个节点负责一部分槽

**配置：**
```bash
# redis.conf
cluster-enabled yes
cluster-config-file nodes.conf
cluster-node-timeout 15000
```

### 22. Redis 集群如何实现高可用？

**答案：**

**1. 主从复制**
- 每个主节点可以有多个从节点
- 主节点故障时，从节点自动提升为主节点

**2. 故障检测**
- 节点间通过 Gossip 协议交换信息
- 超过半数节点认为某节点故障，标记为故障

**3. 故障转移**
- 从节点检测到主节点故障
- 从节点发起选举，成为新的主节点
- 更新槽分配信息

**4. 数据迁移**
- 支持在线添加/删除节点
- 使用 `CLUSTER SETSLOT` 迁移槽
- 支持增量迁移，不影响服务

### 23. Redis 集群的优缺点？

**答案：**

**优点：**
- **水平扩展**：可以动态添加节点
- **高可用**：主从复制 + 自动故障转移
- **数据分片**：数据分布到多个节点
- **无中心化**：每个节点都是对等的

**缺点：**
- **客户端复杂**：需要支持集群协议
- **批量操作限制**：只支持同一槽的 key
- **事务限制**：只支持同一槽的 key
- **配置复杂**：需要管理多个节点

### 24. Redis 集群的槽迁移过程？

**答案：**

**迁移流程：**

**1. 设置迁移状态**
```bash
CLUSTER SETSLOT <slot> IMPORTING <source-node-id>
CLUSTER SETSLOT <slot> MIGRATING <target-node-id>
```

**2. 获取键**
- 目标节点收到请求时，如果 key 正在迁移
- 返回 `ASK` 重定向，客户端访问源节点

**3. 迁移数据**
- 使用 `MIGRATE` 命令迁移 key
- 原子操作，保证数据一致性

**4. 更新槽分配**
- 迁移完成后，更新槽分配信息
- 广播给其他节点

**5. 清理**
- 源节点删除已迁移的 key
- 完成迁移

---

## 性能优化

### 25. 如何优化 Redis 性能？

**答案：**

**1. 合理使用数据结构**
- 根据场景选择合适的数据类型
- 小数据量使用压缩编码

**2. 避免大 key**
- 大 key 会导致：
  - 网络传输慢
  - 内存占用大
  - 阻塞操作时间长
- 解决方案：拆分大 key，使用 Hash 分片

**3. 避免热点 key**
- 热点 key 会导致单节点压力大
- 解决方案：
  - 本地缓存
  - 读写分离
  - 使用 Hash tag 分散到不同节点

**4. 使用 Pipeline**
- 批量执行命令，减少网络往返
- 适合批量操作场景

**5. 使用连接池**
- 复用连接，减少连接开销
- 设置合理的连接池大小

**6. 合理设置过期时间**
- 避免大量 key 同时过期
- 使用随机过期时间

**7. 内存优化**
- 使用合适的数据结构
- 启用压缩
- 定期清理过期 key

### 26. 什么是 Redis 大 key？如何处理？

**答案：**

**大 key 的定义：**
- String 类型：value > 10KB
- Hash/List/Set/ZSet：元素数量 > 5000

**大 key 的危害：**
- **内存占用大**：影响其他 key 的存储
- **网络传输慢**：传输大 key 耗时长
- **阻塞操作**：删除大 key 可能阻塞 Redis
- **主从延迟**：复制大 key 耗时长

**处理方法：**

**1. 拆分大 key**
```bash
# 原：一个大 Hash
HGETALL big_hash

# 拆分为多个小 Hash
HGET small_hash:1 field1
HGET small_hash:2 field2
```

**2. 使用 Hash tag**
```bash
# 使用 {} 保证相关 key 在同一节点
{user:1000}:name
{user:1000}:age
```

**3. 异步删除**
```bash
# Redis 4.0+ 支持异步删除
UNLINK big_key  # 非阻塞删除
```

**4. 定期清理**
- 设置过期时间
- 定期扫描并删除大 key

### 27. 什么是 Redis 热点 key？如何处理？

**答案：**

**热点 key 的定义：**
- 访问频率特别高的 key
- 可能导致单节点压力过大

**检测方法：**
- 使用 `redis-cli --hotkeys` 命令
- 监控 QPS
- 分析访问日志

**处理方法：**

**1. 本地缓存**
- 在应用层缓存热点数据
- 减少对 Redis 的访问

**2. 读写分离**
- 主节点写，从节点读
- 分散读压力

**3. 使用 Hash tag**
- 将热点 key 分散到不同节点
```bash
# 原热点 key
user:1000

# 拆分为多个 key
{user:1000}:info:1
{user:1000}:info:2
```

**4. 限流**
- 对热点 key 的访问进行限流
- 防止缓存击穿

---

## 缓存策略

### 28. 缓存穿透是什么？如何解决？

**答案：**

**缓存穿透：**
- 查询不存在的数据
- 缓存未命中，直接查询数据库
- 大量请求导致数据库压力大

**解决方案：**

**1. 布隆过滤器**
- 使用布隆过滤器判断 key 是否存在
- 不存在直接返回，不查询数据库
- Redis 4.0+ 支持 `BF.ADD` 和 `BF.EXISTS`

**2. 缓存空值**
- 查询不存在的数据时，缓存空值
- 设置较短的过期时间
- 避免重复查询数据库

**3. 参数校验**
- 在应用层校验参数
- 过滤无效请求

**示例：**
```python
def get_user(user_id):
    # 1. 先查缓存
    user = redis.get(f"user:{user_id}")
    if user:
        return user
    
    # 2. 布隆过滤器判断
    if not bloom_filter.exists(user_id):
        return None
    
    # 3. 查数据库
    user = db.get_user(user_id)
    
    # 4. 缓存结果（包括空值）
    if user:
        redis.setex(f"user:{user_id}", 3600, user)
    else:
        redis.setex(f"user:{user_id}", 60, "")  # 缓存空值
    
    return user
```

### 29. 缓存击穿是什么？如何解决？

**答案：**

**缓存击穿：**
- 热点 key 过期
- 大量请求同时查询数据库
- 导致数据库压力瞬间增大

**解决方案：**

**1. 互斥锁**
- 使用分布式锁
- 只有一个线程查询数据库，其他线程等待
- 查询完成后，更新缓存

**2. 热点数据永不过期**
- 热点 key 不设置过期时间
- 后台异步更新缓存

**3. 延迟双删**
- 更新数据库后，删除缓存
- 延迟一段时间后再次删除

**示例：**
```python
def get_hot_data(key):
    # 1. 查缓存
    data = redis.get(key)
    if data:
        return data
    
    # 2. 获取分布式锁
    lock_key = f"lock:{key}"
    if redis.set(lock_key, "1", nx=True, ex=10):
        try:
            # 3. 查数据库
            data = db.get_data(key)
            # 4. 更新缓存
            redis.setex(key, 3600, data)
        finally:
            # 5. 释放锁
            redis.delete(lock_key)
    else:
        # 6. 等待并重试
        time.sleep(0.1)
        return get_hot_data(key)
    
    return data
```

### 30. 缓存雪崩是什么？如何解决？

**答案：**

**缓存雪崩：**
- 大量 key 同时过期
- 大量请求直接查询数据库
- 导致数据库压力过大，甚至崩溃

**解决方案：**

**1. 过期时间随机化**
- 避免大量 key 同时过期
- 在基础过期时间上增加随机值

**2. 多级缓存**
- 本地缓存 + Redis 缓存
- 减少对 Redis 和数据库的压力

**3. 热点数据永不过期**
- 关键数据不设置过期时间
- 后台异步更新

**4. 限流降级**
- 使用限流保护数据库
- 降级返回默认值

**示例：**
```python
import random

def set_cache(key, value, base_ttl=3600):
    # 随机过期时间，避免同时过期
    ttl = base_ttl + random.randint(0, 300)
    redis.setex(key, ttl, value)
```

### 31. 缓存更新策略有哪些？

**答案：**

**1. Cache Aside（旁路缓存）**
- **读**：先查缓存，未命中查数据库，更新缓存
- **写**：更新数据库，删除缓存
- **优点**：简单，数据一致性好
- **缺点**：可能缓存未命中

**2. Write Through（写穿）**
- **写**：同时更新缓存和数据库
- **读**：先查缓存
- **优点**：缓存命中率高
- **缺点**：写操作慢

**3. Write Back（写回）**
- **写**：只更新缓存，异步更新数据库
- **读**：先查缓存
- **优点**：写操作快
- **缺点**：数据可能丢失

**4. Refresh Ahead（提前刷新）**
- 缓存过期前，异步刷新
- 保证缓存命中率
- 适合热点数据

---

## 事务与管道

### 32. Redis 事务是什么？ACID 特性如何？

**答案：**

**Redis 事务：**
- 使用 `MULTI`、`EXEC`、`DISCARD`、`WATCH` 命令
- 将多个命令打包执行

**执行流程：**
```bash
MULTI           # 开始事务
SET key1 value1
SET key2 value2
EXEC            # 执行事务
```

**ACID 特性：**

| 特性 | Redis 支持情况 | 说明 |
|------|--------------|------|
| **原子性** | ✅ | 事务中的命令要么全部执行，要么全部不执行 |
| **一致性** | ✅ | 事务执行前后，数据保持一致 |
| **隔离性** | ✅ | 事务执行过程中，不会被其他命令打断 |
| **持久性** | ⚠️ | 取决于持久化配置（RDB/AOF） |

**注意事项：**
- Redis 事务不支持回滚
- 命令错误会继续执行
- 运行时错误会中断事务

### 33. Redis Pipeline 是什么？

**答案：**

**Pipeline：**
- 批量发送命令，减少网络往返
- 提高性能，特别是网络延迟高的场景

**对比：**

| 方式 | 网络往返 | 性能 |
|------|---------|------|
| **普通模式** | N 次 | 慢 |
| **Pipeline** | 1 次 | 快 |

**使用示例：**
```python
import redis

r = redis.Redis()

# 普通模式
for i in range(100):
    r.set(f"key{i}", f"value{i}")

# Pipeline 模式
pipe = r.pipeline()
for i in range(100):
    pipe.set(f"key{i}", f"value{i}")
pipe.execute()
```

**注意事项：**
- Pipeline 中的命令是原子执行的
- 但不保证事务性
- 适合批量操作场景

---

## 常见问题与解决方案

### 34. Redis 内存满了怎么办？

**答案：**

**1. 增加内存**
- 最简单直接的方法
- 修改 `maxmemory` 配置

**2. 启用内存淘汰策略**
```bash
maxmemory 2gb
maxmemory-policy allkeys-lru
```

**3. 优化数据结构**
- 使用压缩编码
- 避免大 key
- 合理设置过期时间

**4. 使用 Redis 集群**
- 水平扩展，分散内存压力

**5. 清理数据**
- 删除不必要的数据
- 清理过期 key

### 35. Redis 主从延迟怎么解决？

**答案：**

**原因：**
- 主从复制是异步的
- 网络延迟
- 从节点负载高

**解决方案：**

**1. 优化网络**
- 主从节点部署在同一机房
- 使用高速网络

**2. 减少从节点数量**
- 减少主节点复制压力

**3. 使用读写分离**
- 对延迟不敏感的数据从从节点读
- 对实时性要求高的从主节点读

**4. 监控延迟**
- 使用 `INFO replication` 查看延迟
- 设置告警阈值

### 36. Redis 脑裂问题是什么？如何解决？

**答案：**

**脑裂问题：**
- 网络分区导致集群分裂
- 出现多个主节点
- 数据不一致

**场景：**
```
主节点 A
  ├─ 从节点 B
  └─ 从节点 C

网络分区：
分区1: A, B
分区2: C

结果：
- 分区1：A 仍是主节点，可以写
- 分区2：C 提升为主节点，也可以写
- 数据不一致！
```

**解决方案：**

**1. 最少从节点数**
```bash
min-replicas-to-write 1
min-replicas-max-lag 10
```
- 主节点至少要有 N 个从节点
- 从节点延迟不能超过指定值
- 否则主节点拒绝写操作

**2. 合理设置超时时间**
```bash
cluster-node-timeout 15000
```
- 节点超时时间
- 超过时间认为节点故障

**3. 使用 Redis Sentinel**
- 哨兵模式可以更好地处理脑裂

### 37. Redis 如何实现分布式锁？

**答案：**

**基本实现：**
```bash
# 加锁
SET lock_key unique_value NX EX 10

# 解锁（Lua 脚本保证原子性）
if redis.call("get", KEYS[1]) == ARGV[1] then
    return redis.call("del", KEYS[1])
else
    return 0
end
```

**关键点：**

**1. 唯一值**
- 使用唯一标识（如 UUID）
- 防止误删其他客户端的锁

**2. 过期时间**
- 设置过期时间，防止死锁
- 使用 `EX` 参数

**3. 原子性**
- 使用 `SET NX` 保证原子性
- 解锁使用 Lua 脚本

**4. 续期**
- 使用看门狗机制续期
- 防止业务执行时间超过锁的过期时间

**Redlock 算法：**
- 在多个 Redis 实例上获取锁
- 超过半数实例获取成功才算成功
- 提高可靠性

**示例：**
```python
import redis
import uuid
import time

class DistributedLock:
    def __init__(self, redis_client, key, timeout=10):
        self.redis = redis_client
        self.key = key
        self.timeout = timeout
        self.identifier = str(uuid.uuid4())
    
    def acquire(self):
        end = time.time() + self.timeout
        while time.time() < end:
            if self.redis.set(self.key, self.identifier, nx=True, ex=self.timeout):
                return True
            time.sleep(0.001)
        return False
    
    def release(self):
        lua = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        return self.redis.eval(lua, 1, self.key, self.identifier)
```

---

## 高级特性

### 38. Redis 的发布订阅（Pub/Sub）是什么？

**答案：**

**发布订阅模式：**
- 发布者（Publisher）发送消息
- 订阅者（Subscriber）接收消息
- 解耦发布者和订阅者

**基本命令：**
```bash
# 订阅频道
SUBSCRIBE channel1 channel2

# 发布消息
PUBLISH channel1 "Hello World"

# 模式订阅
PSUBSCRIBE news.*

# 取消订阅
UNSUBSCRIBE channel1
```

**特点：**
- **非持久化**：消息不持久化，订阅者离线会丢失
- **无消息队列**：没有消息队列，不能保证消息送达
- **广播**：所有订阅者都能收到消息

**应用场景：**
- 实时消息推送
- 事件通知
- 系统解耦

**与 Stream 对比：**
- Pub/Sub：简单，但不持久化
- Stream：复杂，但支持持久化和消费者组

### 39. Redis 的 Lua 脚本是什么？

**答案：**

**Lua 脚本：**
- Redis 支持执行 Lua 脚本
- 保证原子性执行
- 减少网络往返

**基本使用：**
```bash
# 执行脚本
EVAL "return redis.call('get', KEYS[1])" 1 mykey

# 加载脚本
SCRIPT LOAD "return redis.call('get', KEYS[1])"

# 执行已加载的脚本
EVALSHA <sha1> 1 mykey
```

**优势：**
- **原子性**：脚本执行是原子的
- **性能**：减少网络往返
- **灵活性**：可以实现复杂逻辑

**应用场景：**
- 分布式锁解锁
- 原子性操作
- 复杂业务逻辑

**注意事项：**
- 脚本执行时间不能太长
- 不能执行阻塞命令
- 使用 `SCRIPT KILL` 可以终止脚本

### 40. Redis 的慢查询日志是什么？

**答案：**

**慢查询日志：**
- 记录执行时间超过阈值的命令
- 帮助定位性能问题

**配置：**
```bash
# redis.conf
slowlog-log-slower-than 10000  # 超过10ms记录（微秒）
slowlog-max-len 128            # 最多记录128条
```

**查看慢查询：**
```bash
# 查看慢查询日志
SLOWLOG GET 10

# 获取慢查询日志数量
SLOWLOG LEN

# 清空慢查询日志
SLOWLOG RESET
```

**分析慢查询：**
- 检查命令执行时间
- 分析命令参数
- 优化数据结构
- 使用索引

### 41. Redis 的内存优化技巧？

**答案：**

**1. 使用合适的数据结构**
- 小数据量使用压缩编码
- 根据场景选择数据类型

**2. 共享对象池**
```bash
# redis.conf
# 共享对象池，节省内存
object-sharing-pool-size 1024
```

**3. 使用 Hash 代替 String**
- 多个相关字段使用 Hash
- 比多个 String 节省内存

**4. 压缩列表配置**
```bash
# 优化压缩列表阈值
hash-max-ziplist-entries 512
hash-max-ziplist-value 64
list-max-ziplist-size -2
```

**5. 定期清理**
- 设置合理的过期时间
- 定期清理无用数据

**6. 内存分析**
```bash
# 查看内存使用
INFO memory

# 分析 key 的内存占用
MEMORY USAGE key

# 内存分析工具
redis-memory-for-key
```

### 42. Redis 6.0 多线程是什么？

**答案：**

**多线程 I/O：**
- Redis 6.0 引入了多线程 I/O
- 命令执行仍是单线程
- 只多线程处理网络 I/O

**架构：**
```
主线程（单线程）
  ├─ 接收连接
  ├─ 解析命令
  ├─ 执行命令（单线程）
  └─ 返回结果

I/O 线程（多线程）
  ├─ 读取数据
  └─ 写入数据
```

**配置：**
```bash
# redis.conf
io-threads 4              # I/O 线程数
io-threads-do-reads yes   # 启用多线程读
```

**优势：**
- 提高网络 I/O 性能
- 充分利用多核 CPU
- 保持命令执行的原子性

**注意事项：**
- 只对网络 I/O 有效
- 命令执行仍是单线程
- 需要根据 CPU 核心数配置

### 43. Redis 的监控指标有哪些？

**答案：**

**关键指标：**

**1. 性能指标**
- **QPS**：每秒查询数
- **延迟**：命令执行时间
- **吞吐量**：每秒处理的字节数

**2. 内存指标**
- **使用量**：当前内存使用
- **峰值**：历史最大使用量
- **碎片率**：内存碎片比例

**3. 连接指标**
- **连接数**：当前连接数
- **拒绝连接数**：被拒绝的连接数

**4. 复制指标**
- **主从延迟**：复制延迟
- **复制积压缓冲区**：缓冲区大小

**监控命令：**
```bash
# 查看所有信息
INFO

# 查看内存信息
INFO memory

# 查看复制信息
INFO replication

# 查看客户端信息
INFO clients

# 实时监控命令
MONITOR
```

**监控工具：**
- **redis-cli**：命令行工具
- **RedisInsight**：可视化工具
- **Prometheus + Grafana**：监控系统
- **redis-stat**：实时监控工具

### 44. Redis 的安全配置？

**答案：**

**安全措施：**

**1. 密码认证**
```bash
# redis.conf
requirepass your_password
```

**2. 绑定 IP**
```bash
# 只允许本地访问
bind 127.0.0.1

# 或指定 IP
bind 192.168.1.100
```

**3. 禁用危险命令**
```bash
# redis.conf
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command CONFIG "CONFIG_9c5d2f8b"
```

**4. 使用非 root 用户运行**
```bash
# 创建 Redis 用户
useradd -r -s /bin/false redis

# 使用该用户运行
su - redis -s /bin/bash
```

**5. 网络隔离**
- 使用防火墙限制访问
- 使用 VPN 或专网

**6. TLS 加密**
```bash
# redis.conf
tls-port 6380
tls-cert-file redis.crt
tls-key-file redis.key
```

**7. ACL（访问控制列表）**
```bash
# Redis 6.0+
ACL SETUSER alice on >password ~cached:* +get
```

### 45. Redis 与其他缓存对比？

**答案：**

**Redis vs Memcached：**

| 特性 | Redis | Memcached |
|------|-------|-----------|
| 数据类型 | 丰富（8种） | 简单（String） |
| 持久化 | 支持 | 不支持 |
| 主从复制 | 支持 | 不支持 |
| 集群 | 支持 | 不支持 |
| 性能 | 高 | 极高 |
| 内存效率 | 中等 | 高 |

**Redis vs MongoDB：**

| 特性 | Redis | MongoDB |
|------|-------|---------|
| 数据模型 | 键值对 | 文档 |
| 持久化 | 可选 | 必须 |
| 查询能力 | 简单 | 强大 |
| 适用场景 | 缓存、队列 | 数据库 |

**选择建议：**
- **缓存场景**：Redis
- **简单键值存储**：Memcached
- **复杂查询**：MongoDB
- **消息队列**：Redis Stream

---

## 总结

Redis 是一个功能强大的内存数据库，掌握其核心概念、数据结构、持久化机制、高可用方案和性能优化技巧，对于构建高性能、高可用的系统至关重要。

**关键要点：**
- **数据结构**：根据场景选择合适的数据类型
- **持久化**：RDB + AOF 结合使用
- **高可用**：主从复制 + 哨兵/集群
- **性能优化**：避免大 key、热点 key，合理使用 Pipeline
- **缓存策略**：防止穿透、击穿、雪崩
- **安全配置**：密码认证、网络隔离、ACL

持续学习 Redis 的新特性和最佳实践，结合实际业务场景优化配置，是成为 Redis 专家的关键。
