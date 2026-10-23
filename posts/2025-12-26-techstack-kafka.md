---
title: "Kafka 面试高频考点精讲"
date: 2025-12-26
main: "中间件"
sub: ["kafka", "message-queue", "streaming"]
summary: "围绕 Kafka 面试高频问题，聚焦核心概念、分区副本、ISR、生产消费、可靠性与性能优化，按面试口径整理。"
---

# Kafka 面试高频考点精讲

这篇不追求“百科全书式介绍”，只按面试场景讲高频问题、核心结论和常见追问。

---

## 1. Kafka 是什么？适合什么场景？

**面试口径：**

Kafka 本质上是一个**分布式日志系统 + 高吞吐消息系统 + 流式数据平台**。

最适合三类场景：

1. **异步解耦**
2. **日志/埋点/事件采集**
3. **流式计算的数据入口**

**核心特点：**

- 高吞吐，依赖顺序写、批量发送、批量拉取、零拷贝
- 分布式，天然支持分区扩展
- 持久化，消息落盘
- 高可用，依赖副本和 ISR

**一句话区分：**

- 如果重点是**海量数据吞吐、日志流、事件流**，Kafka 很合适
- 如果重点是**复杂路由、低吞吐但强业务语义**，RabbitMQ 这类更常见

---

## 2. Kafka 为什么快？

这是 Kafka 面试最常见的问题之一。

**标准回答：**

Kafka 快，核心不是“都在内存里”，而是**把磁盘和网络都尽量按顺序、批量、少拷贝地使用**。

**关键点：**

### 2.1 顺序写

Kafka 的消息是追加写日志文件，顺序写磁盘比随机写快得多。

### 2.2 Page Cache

Kafka 大量依赖操作系统页缓存。生产者写入时，数据通常先进入页缓存；消费者读取热点数据时，也可能直接命中缓存。

### 2.3 零拷贝

Kafka 发送消息给消费者时可用 `sendfile`，减少用户态和内核态之间的数据复制。

### 2.4 批量

- Producer 批量发送
- Broker 批量刷盘
- Consumer 批量拉取

批量意味着更少的网络往返和更高的吞吐。

### 2.5 分区并行

一个 Topic 可以拆成多个 Partition，在多个 Broker 和多个 Consumer 上并行处理。

**面试结论：**

Kafka 的快是**顺序 I/O + 批量 + Page Cache + 零拷贝 + 分区并行**共同作用的结果。

---

## 3. Topic、Partition、Broker 分别是什么？

### 3.1 Topic

逻辑上的消息分类。

### 3.2 Partition

Topic 的物理分片。Kafka 的扩展性和并发能力主要靠 Partition。

### 3.3 Broker

Kafka 集群里的单个节点，负责存储分区和处理读写请求。

**面试要点：**

- Topic 是逻辑概念
- Partition 才是并行和扩展的最小单位
- Broker 是实际存储和服务节点

---

## 4. Partition 为什么重要？

Partition 是 Kafka 的核心。

**它解决三个问题：**

1. **扩展性**：一个 Topic 可以横向拆分到多个 Broker
2. **吞吐量**：不同 Partition 可以并发读写
3. **消费组负载均衡**：不同 Consumer 可消费不同 Partition

**但要注意：**

- Kafka 只保证**单 Partition 内有序**
- 多 Partition 之间**不保证全局有序**

这点很容易被追问。

**如果业务要严格有序怎么办？**

- 把同一业务键（如订单 ID、用户 ID）路由到同一 Partition
- 或者退化成单 Partition，但吞吐会受限

---

## 5. Kafka 怎么保证消息有序？

**标准回答：**

Kafka 只能保证**同一个 Partition 内的消息有序**。

前提通常是：

- 同一类业务消息使用同一个 key
- Producer 根据 key 进入同一个 Partition
- Consumer 按分区顺序消费

**不能误答成：Kafka 全局有序。**

如果 Topic 有多个 Partition，不同 Partition 之间是并行消费的，不存在全局顺序。

---

## 6. 副本机制是什么？Leader 和 Follower 怎么工作？

Kafka 每个 Partition 可以配置多个副本。

### 6.1 Leader

- 所有读写都走 Leader

### 6.2 Follower

- 从 Leader 拉取数据，追赶日志
- 正常情况下不直接对外提供写服务

**关键结论：**

- Producer 只写 Leader
- Consumer 默认只读 Leader
- Follower 的价值在于高可用，不是分担读流量

---

## 7. 什么是 ISR？为什么它很关键？

ISR = **In-Sync Replicas**，表示和 Leader 保持同步的一组副本。

**面试口径：**

Kafka 不是简单地“所有副本都算有效”，而是只认为 ISR 里的副本是可靠副本。

如果某个 Follower 落后太多，就会被踢出 ISR。

**为什么重要？**

Leader 故障时，新 Leader 一般从 ISR 中选。

这样做的目的就是：

- 避免选到太落后的副本
- 降低数据丢失风险

**高频追问：**

为什么不用所有副本都参与选主？

因为落后太多的副本即使“活着”，也可能数据不完整。选它做 Leader 会造成更严重的数据回退。

---

## 8. acks 有什么作用？

Producer 的 `acks` 决定发送确认级别。

### 8.1 `acks=0`

- Producer 发完不等确认
- 吞吐高
- 最不可靠

### 8.2 `acks=1`

- Leader 写入成功就返回
- Leader 还没同步给 Follower 就宕机的话，可能丢消息

### 8.3 `acks=all` 或 `-1`

- 需要 ISR 中满足要求的副本都确认
- 可靠性最高

**面试结论：**

如果追求可靠性，通常回答：

- `acks=all`
- 配合 `min.insync.replicas`
- 再配合 Producer 重试和幂等

这样才是完整答案。

---

## 9. `acks=all` 就一定不丢消息吗？

**标准回答：不一定。**

因为还要看：

- `min.insync.replicas` 配多少
- ISR 里实际还有几个副本
- 是否开启幂等和重试
- Consumer 侧 offset 提交策略

**举例：**

如果副本数是 3，但 `min.insync.replicas=1`，那 ISR 里只要 Leader 自己还在，也可能成功返回。这种情况下可靠性并没有你想象得那么高。

---

## 10. `min.insync.replicas` 是什么？

它定义的是：

在 `acks=all` 的情况下，至少需要多少个 ISR 副本确认，写入才算成功。

**经典配置：**

- replication.factor = 3
- min.insync.replicas = 2
- acks = all

这是一套很常见的生产配置。

**意义：**

即使挂掉一个副本，系统仍然可以继续提供可靠写入。

---

## 11. 什么情况下会丢消息？

这是 Kafka 面试必答题。

### 11.1 Producer 侧

- `acks=0`
- 未正确重试
- 网络抖动导致发送失败但业务未感知

### 11.2 Broker 侧

- `acks=1` 时 Leader 刚写完就宕机，还没同步到 Follower
- ISR 设置过宽，导致选主时拿到的数据不够新

### 11.3 Consumer 侧

- 先提交 offset，再处理消息，处理过程中宕机，会丢消费
- 自动提交 offset 时机不合适

**面试回答模板：**

Kafka 不丢消息要同时看三段：

- Producer 是否可靠发送
- Broker 是否可靠落盘和副本同步
- Consumer 是否正确提交 offset

只答 Broker 不够。

---

## 12. Kafka 会不会重复消费？

**会。**

Kafka 默认语义更接近 **at least once**。

出现重复消费的典型场景：

- Consumer 处理成功了，但 offset 还没提交就宕机
- 重平衡后某些消息被再次消费
- Producer 重试导致重复写入

**怎么处理？**

### 12.1 Consumer 幂等

业务层做去重，例如：

- 数据库唯一键
- 幂等表
- 去重状态表

### 12.2 Producer 幂等

开启 `enable.idempotence=true`

它能减少因为网络重试造成的重复写入。

**面试结论：**

Kafka 本身很难天然保证“业务绝对不重复”，最终还是要靠业务幂等兜底。

---

## 13. Kafka 怎么实现“恰好一次”？

这是高频进阶题。

**标准回答：**

Kafka 在特定场景下支持 EOS（Exactly Once Semantics），主要依赖：

1. **幂等 Producer**
2. **事务消息**
3. **消费-处理-生产链路的一致提交**

**但要讲清楚边界：**

- 这是 Kafka 体系内的“恰好一次”
- 如果落到外部数据库、缓存、第三方服务，仍然要自己处理幂等

不要把它答成“Kafka 在所有业务场景都能保证 exactly once”。

---

## 14. Consumer Group 是怎么工作的？

一个 Consumer Group 内：

- 一个 Partition 同一时刻只能被组内一个 Consumer 消费
- 多个 Partition 可以分配给多个 Consumer

**结论：**

- Consumer Group 提供的是**广播之外的负载均衡消费能力**
- 扩容 Consumer 数量的上限，本质上受 Partition 数量限制

**常见追问：**

如果 Consumer 数量大于 Partition 数量会怎样？

答案：

- 多出来的 Consumer 会空闲

---

## 15. Rebalance 是什么？为什么要关注？

Rebalance 是消费组内重新分配 Partition 的过程。

触发场景通常有：

- Consumer 增减
- Consumer 宕机/恢复
- Topic Partition 数变化

**为什么麻烦？**

Rebalance 期间会影响消费连续性，处理不好会带来：

- 消费暂停
- 重复消费
- 延迟抖动

**优化方向：**

- 降低无意义的 Consumer 抖动
- 控制单次处理时间，避免被误判超时
- 理解 `session.timeout.ms`、`max.poll.interval.ms`

---

## 16. Kafka 的消费者是推还是拉？

**拉模式。**

Consumer 主动向 Broker 拉取数据。

**为什么 Kafka 选择拉模式？**

- Consumer 自己控制消费速率
- 更适合不同消费能力的客户端
- 批量拉取更容易做吞吐优化

---

## 17. Offset 提交什么时候最合理？

**标准回答：**

通常是**消息处理成功后再提交 offset**。

如果先提交再处理，Consumer 宕机后，这条消息就可能再也不会被消费，属于消息丢失。

### 自动提交的问题

- 简单
- 但容易在“还没处理完”时就提交掉

### 手动提交的优势

- 可控
- 更适合重要业务

**面试建议：**

重要业务优先答：**手动提交 + 处理成功后提交**。

---

## 18. Kafka 积压了怎么办？

这是非常实战的题。

**先判断瓶颈在哪：**

1. Producer 太快
2. Consumer 太慢
3. 下游依赖慢
4. Partition 不够导致并行度不足

**常见处理手段：**

### 18.1 增加 Consumer 实例

前提是 Partition 足够多。

### 18.2 增加 Partition

提升并行度，但要注意扩容后数据分布变化和顺序性影响。

### 18.3 优化消费逻辑

- 批处理
- 减少同步阻塞
- 异步化下游操作

### 18.4 临时跳过历史低优先级数据

只适合允许降级的场景，不是通用方案。

**面试重点：**

不要只说“加机器”，要说明积压本质是**生产速度 > 消费速度**，要定位瓶颈点。

---

## 19. Kafka 常见性能调优点有哪些？

### Producer 侧

- `batch.size`
- `linger.ms`
- `compression.type`
- `buffer.memory`

### Broker 侧

- 合理设置 Partition 数
- 合理设置副本数
- 磁盘选择和 I/O 能力
- Page Cache 命中情况

### Consumer 侧

- `fetch.min.bytes`
- `max.poll.records`
- 批量处理
- 降低 Rebalance 频率

**面试一句话：**

Kafka 调优不是只调一个参数，而是围绕**吞吐、延迟、可靠性**做平衡。

---

## 20. Kafka 和 RocketMQ / RabbitMQ 怎么选？

### 20.1 Kafka

适合：

- 日志采集
- 埋点数据
- 事件流
- 高吞吐异步链路

### 20.2 RabbitMQ

适合：

- 传统业务消息
- 复杂路由
- 对协议和消费模型要求灵活的系统

### 20.3 RocketMQ

适合：

- 业务消息系统
- 顺序消息、事务消息需求更强的场景

**面试建议：**

不要答成“谁更强”，而要答成“取决于业务目标”。

---

## 21. Kafka 面试收尾时的总结答法

如果面试官让你总结 Kafka，可以这样收口：

> Kafka 的核心是分区日志模型。它通过顺序写、批量、零拷贝和页缓存做到高吞吐；通过副本、ISR、Leader/Follower 提供高可用；通过 Consumer Group 提供并发消费能力。实际使用里最关键的是理解顺序性边界、可靠性配置、重复消费和积压处理。

这段总结比背定义更像真正做过系统的人。
