---
title: "Canal 详解：MySQL Binlog 增量订阅与消费组件"
date: 2025-12-27
main: "数据库"
sub: ["canal", "mysql", "binlog", "cdc", "data-sync"]
summary: "深入讲解 Canal，阿里巴巴开源的 MySQL binlog 增量订阅与消费组件，包括工作原理、架构设计、使用场景、配置部署等"
---

# Canal 详解：MySQL Binlog 增量订阅与消费组件

## 什么是 Canal？

Canal 是阿里巴巴开源的基于 MySQL binlog 的增量订阅&消费组件，主要用于数据库变更数据捕获（CDC - Change Data Capture）。

**核心功能：**
- **增量订阅**：实时订阅 MySQL binlog
- **数据同步**：将数据库变更同步到其他系统
- **解耦系统**：数据库和下游系统解耦

**项目地址：**
- GitHub: https://github.com/alibaba/canal
- 官方文档: https://github.com/alibaba/canal/wiki

---

## 目录

- [为什么需要 Canal？](#为什么需要-canal)
- [工作原理](#工作原理)
- [架构设计](#架构设计)
- [核心概念](#核心概念)
- [使用场景](#使用场景)
- [快速开始](#快速开始)
- [配置详解](#配置详解)
- [高级特性](#高级特性)
- [与其他工具对比](#与其他工具对比)
- [常见问题](#常见问题)
- [总结](#总结)

---

## 为什么需要 Canal？

### 传统数据同步的问题

**1. 轮询查询**
```sql
-- 应用需要定期查询数据库
SELECT * FROM users WHERE update_time > ?
```
**问题：**
- 实时性差
- 数据库压力大
- 可能遗漏数据

**2. 触发器**
```sql
-- 使用数据库触发器
CREATE TRIGGER user_update AFTER UPDATE ON users
FOR EACH ROW
BEGIN
    -- 同步到其他系统
END;
```
**问题：**
- 影响数据库性能
- 耦合度高
- 难以维护

**3. 双写**
```java
// 应用同时写入数据库和缓存
userService.save(user);  // 写入数据库
cacheService.save(user); // 写入缓存
```
**问题：**
- 数据不一致风险
- 代码复杂
- 难以保证原子性

### Canal 的优势

**1. 实时性**
- 基于 binlog，实时捕获变更
- 延迟通常在毫秒级

**2. 解耦**
- 数据库和下游系统完全解耦
- 不影响数据库性能

**3. 可靠性**
- 基于 binlog，数据完整可靠
- 支持断点续传

**4. 灵活性**
- 支持多种下游系统（Kafka、RocketMQ、Elasticsearch 等）
- 支持过滤和转换

---

## 工作原理

### MySQL Binlog 基础

**Binlog（Binary Log）** 是 MySQL 的二进制日志，记录所有数据变更操作。

**Binlog 格式：**

**1. STATEMENT（语句模式）**
- 记录 SQL 语句
- 优点：日志量小
- 缺点：可能不一致（如 NOW()、RAND()）

**2. ROW（行模式）**
- 记录每行数据的变化
- 优点：数据一致性强
- 缺点：日志量大
- **Canal 主要使用 ROW 模式**

**3. MIXED（混合模式）**
- 自动选择 STATEMENT 或 ROW

**Binlog 事件类型：**
- `QUERY_EVENT`：DDL 语句
- `TABLE_MAP_EVENT`：表映射
- `WRITE_ROWS_EVENT`：INSERT
- `UPDATE_ROWS_EVENT`：UPDATE
- `DELETE_ROWS_EVENT`：DELETE

### Canal 工作流程

```
MySQL Master
    ↓ (开启 binlog)
Binlog 文件
    ↓ (Canal 模拟 Slave)
Canal Server
    ↓ (解析 binlog)
Canal Client
    ↓ (消费数据)
下游系统（Kafka、ES、缓存等）
```

**详细流程：**

**1. Canal 模拟 MySQL Slave**
- Canal 作为 MySQL 的 Slave
- 向 MySQL Master 发送 dump 请求
- MySQL Master 推送 binlog 给 Canal

**2. Canal 解析 Binlog**
- 接收 binlog 事件
- 解析为结构化数据
- 转换为 Canal 的 Entry 格式

**3. Canal 存储和转发**
- 存储到本地（可选）
- 转发给 Canal Client
- 支持多种协议（TCP、Kafka、RocketMQ 等）

**4. Canal Client 消费**
- 订阅 Canal Server
- 接收变更数据
- 同步到下游系统

---

## 架构设计

### Canal 架构图

```
┌─────────────────┐
│   MySQL Master  │
│   (开启 binlog)  │
└────────┬────────┘
         │ binlog
         ↓
┌─────────────────┐
│  Canal Server   │
│  (模拟 Slave)   │
│  - 接收 binlog   │
│  - 解析 binlog   │
│  - 存储/转发     │
└────────┬────────┘
         │ Entry
         ↓
┌─────────────────┐
│  Canal Client   │
│  - 订阅 Canal    │
│  - 消费数据      │
│  - 同步下游      │
└────────┬────────┘
         │
    ┌────┴────┬──────────┬──────────┐
    ↓         ↓          ↓          ↓
  Kafka    RocketMQ   Elasticsearch  Redis
```

### 核心组件

**1. Canal Server**
- **功能**：接收和解析 binlog
- **部署**：独立部署，不依赖应用
- **配置**：连接 MySQL，配置实例

**2. Canal Client**
- **功能**：消费 Canal Server 的数据
- **部署**：可以部署在应用服务器
- **配置**：连接 Canal Server，配置消费逻辑

**3. Canal Admin**
- **功能**：管理 Canal Server
- **功能**：监控、配置、运维

### 数据模型

**Entry（条目）**
```java
Entry {
    Header {
        version        // 版本
        logfileName    // binlog 文件名
        logfileOffset  // binlog 位置
        serverId       // 服务器 ID
        serverenCode   // 服务器编码
        executeTime    // 执行时间
        sourceType     // 来源类型（MYSQL）
        schemaName     // 数据库名
        tableName      // 表名
        eventType      // 事件类型（INSERT/UPDATE/DELETE）
    }
    EntryType         // 事务开始/数据变更/事务结束
    StoreValue        // 序列化后的数据
}
```

**RowChange（行变更）**
```java
RowChange {
    tableId          // 表 ID
    eventType        // 事件类型
    isDdl            // 是否 DDL
    sql              // SQL 语句
    rowDatas[]       // 行数据
}
```

**RowData（行数据）**
```java
RowData {
    beforeColumns[]  // 变更前的列
    afterColumns[]   // 变更后的列
}
```

---

## 核心概念

### 1. Instance（实例）

**定义：** Canal 的一个数据同步任务，对应一个 MySQL 数据源。

**配置：**
```properties
# conf/canal.properties
canal.instance.master.address = 127.0.0.1:3306
canal.instance.master.journal.name =
canal.instance.master.position =
canal.instance.master.timestamp =
```

**特点：**
- 一个 Canal Server 可以配置多个 Instance
- 每个 Instance 独立运行
- 可以配置不同的过滤规则

### 2. Destination（目的地）

**定义：** Canal Client 订阅的目标，对应一个 Instance。

**使用：**
```java
CanalConnector connector = CanalConnectors.newSingleConnector(
    new InetSocketAddress("127.0.0.1", 11111),
    "example",  // destination
    "",         // username
    ""          // password
);
```

### 3. Position（位置）

**定义：** Canal 消费 binlog 的位置，用于断点续传。

**存储：**
- **内存模式**：存储在内存，重启丢失
- **文件模式**：存储在文件，支持持久化
- **ZooKeeper 模式**：存储在 ZooKeeper，支持集群

**格式：**
```
journalName + position
例如：mysql-bin.000001:1234
```

### 4. Filter（过滤）

**定义：** 过滤规则，只同步指定的数据库和表。

**配置：**
```properties
# 只同步 test 数据库的 t_user 表
canal.instance.filter.regex = test\\.t_user
```

**规则：**
- 支持正则表达式
- 多个规则用逗号分隔
- `.*\\..*` 表示所有表

---

## 使用场景

### 1. 数据库同步

**场景：** 主从数据库同步

```
MySQL Master → Canal → MySQL Slave
```

**应用：**
- 异地多活
- 读写分离
- 数据备份

### 2. 缓存更新

**场景：** 数据库变更自动更新缓存

```
MySQL → Canal → Redis/Cache
```

**优势：**
- 自动更新，无需应用代码
- 保证缓存一致性
- 解耦应用和缓存

### 3. 搜索引擎同步

**场景：** 数据库变更同步到搜索引擎

```
MySQL → Canal → Elasticsearch/Solr
```

**应用：**
- 商品搜索
- 内容搜索
- 日志搜索

### 4. 数据仓库同步

**场景：** 实时数据同步到数据仓库

```
MySQL → Canal → Kafka → 数据仓库
```

**应用：**
- 实时 ETL
- 数据湖
- 数据分析

### 5. 消息队列

**场景：** 数据库变更作为消息发送

```
MySQL → Canal → Kafka/RocketMQ
```

**应用：**
- 事件驱动架构
- 微服务通信
- 异步处理

### 6. 监控和审计

**场景：** 记录所有数据变更

```
MySQL → Canal → 审计系统
```

**应用：**
- 操作审计
- 数据变更追踪
- 合规性要求

---

## 快速开始

### 1. 环境准备

**MySQL 配置：**
```sql
-- 开启 binlog
[mysqld]
log-bin=mysql-bin
binlog-format=ROW
server-id=1

-- 创建 Canal 用户
CREATE USER 'canal'@'%' IDENTIFIED BY 'canal';
GRANT SELECT, REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'canal'@'%';
FLUSH PRIVILEGES;
```

### 2. 下载 Canal

```bash
# 下载 Canal
wget https://github.com/alibaba/canal/releases/download/canal-1.1.7/canal.deployer-1.1.7.tar.gz

# 解压
tar -xzf canal.deployer-1.1.7.tar.gz
cd canal
```

### 3. 配置 Canal Server

**修改 conf/canal.properties：**
```properties
canal.port = 11111
canal.instance.master.address = 127.0.0.1:3306
canal.instance.master.journal.name =
canal.instance.master.position =
canal.instance.master.timestamp =
canal.instance.dbUsername = canal
canal.instance.dbPassword = canal
```

**修改 conf/example/instance.properties：**
```properties
canal.instance.master.address = 127.0.0.1:3306
canal.instance.dbUsername = canal
canal.instance.dbPassword = canal
canal.instance.filter.regex = .*\\..*
```

### 4. 启动 Canal Server

```bash
# 启动
sh bin/startup.sh

# 查看日志
tail -f logs/canal/canal.log
```

### 5. 编写 Canal Client

**Maven 依赖：**
```xml
<dependency>
    <groupId>com.alibaba.otter</groupId>
    <artifactId>canal.client</artifactId>
    <version>1.1.7</version>
</dependency>
```

**Java 代码：**
```java
public class CanalClient {
    public static void main(String[] args) {
        // 创建连接
        CanalConnector connector = CanalConnectors.newSingleConnector(
            new InetSocketAddress("127.0.0.1", 11111),
            "example",
            "",
            ""
        );
        
        try {
            connector.connect();
            connector.subscribe(".*\\..*");
            connector.rollback();
            
            while (true) {
                Message message = connector.getWithoutAck(100);
                long batchId = message.getId();
                int size = message.getEntries().size();
                
                if (batchId == -1 || size == 0) {
                    Thread.sleep(1000);
                } else {
                    printEntry(message.getEntries());
                    connector.ack(batchId);
                }
            }
        } finally {
            connector.disconnect();
        }
    }
    
    private static void printEntry(List<Entry> entries) {
        for (Entry entry : entries) {
            if (entry.getEntryType() == EntryType.ROWDATA) {
                RowChange rowChange = CanalEntry.RowChange.parseFrom(entry.getStoreValue());
                EventType eventType = rowChange.getEventType();
                
                System.out.println("数据库: " + entry.getHeader().getSchemaName());
                System.out.println("表: " + entry.getHeader().getTableName());
                System.out.println("事件类型: " + eventType);
                
                for (RowData rowData : rowChange.getRowDatasList()) {
                    if (eventType == EventType.DELETE) {
                        printColumn(rowData.getBeforeColumnsList());
                    } else if (eventType == EventType.INSERT) {
                        printColumn(rowData.getAfterColumnsList());
                    } else {
                        System.out.println("---变更前---");
                        printColumn(rowData.getBeforeColumnsList());
                        System.out.println("---变更后---");
                        printColumn(rowData.getAfterColumnsList());
                    }
                }
            }
        }
    }
    
    private static void printColumn(List<Column> columns) {
        for (Column column : columns) {
            System.out.println(column.getName() + " : " + column.getValue() + 
                             "    update=" + column.getUpdated());
        }
    }
}
```

---

## 配置详解

### Canal Server 配置

**conf/canal.properties：**
```properties
# Canal Server 端口
canal.port = 11111

# Canal Server 模式（tcp, kafka, rocketMQ, rabbitMQ）
canal.serverMode = tcp

# Instance 列表
canal.destinations = example

# 数据存储模式（memory, file, zookeeper）
canal.instance.global.mode = memory
canal.instance.global.lazy = false
```

### Instance 配置

**conf/example/instance.properties：**
```properties
# MySQL 地址
canal.instance.master.address = 127.0.0.1:3306

# MySQL 用户名密码
canal.instance.dbUsername = canal
canal.instance.dbPassword = canal

# 过滤规则
canal.instance.filter.regex = .*\\..*

# 存储模式
canal.instance.mode = memory

# 批量大小
canal.instance.transaction.size = 1024
```

### Kafka 模式配置

**conf/canal.properties：**
```properties
# 使用 Kafka 模式
canal.serverMode = kafka

# Kafka 配置
kafka.bootstrap.servers = 127.0.0.1:9092
kafka.acks = all
kafka.compression.type = none
kafka.batch.size = 16384
kafka.linger.ms = 1
```

**conf/example/instance.properties：**
```properties
# Kafka Topic
canal.mq.topic = example
canal.mq.partition = 0
```

---

## 高级特性

### 1. 集群部署

**ZooKeeper 模式：**
```properties
# 使用 ZooKeeper 存储 Position
canal.instance.global.mode = zookeeper
canal.instance.global.zkServers = 127.0.0.1:2181
```

**优势：**
- 支持多 Canal Server 部署
- 自动故障转移
- Position 持久化

### 2. 数据过滤

**按数据库过滤：**
```properties
canal.instance.filter.regex = test\\..*
```

**按表过滤：**
```properties
canal.instance.filter.regex = test\\.t_user,test\\.t_order
```

**按字段过滤：**
- 需要在 Client 端实现
- 解析 RowData，过滤字段

### 3. 数据转换

**自定义转换：**
```java
// 在 Client 端转换数据格式
RowData rowData = ...;
Map<String, Object> data = convertToMap(rowData);
String json = JSON.toJSONString(data);
```

### 4. 监控和告警

**Canal Admin：**
- Web 界面管理
- 监控 Canal Server 状态
- 配置管理

**Metrics：**
- 消费延迟
- 消费速度
- 错误率

---

## 与其他工具对比

### Canal vs Debezium

| 特性 | Canal | Debezium |
|------|-------|----------|
| **开发公司** | 阿里巴巴 | Red Hat |
| **支持数据库** | MySQL | MySQL、PostgreSQL、MongoDB 等 |
| **协议** | 自定义协议 | Kafka Connect |
| **易用性** | 简单 | 需要 Kafka |
| **社区** | 国内活跃 | 国际活跃 |

### Canal vs Maxwell

| 特性 | Canal | Maxwell |
|------|-------|---------|
| **开发公司** | 阿里巴巴 | Zendesk |
| **输出格式** | Entry | JSON |
| **存储** | 支持多种 | 主要 Kafka |
| **配置** | 相对复杂 | 简单 |

### 选择建议

- **Canal**：国内项目，需要灵活配置
- **Debezium**：需要多数据库支持，使用 Kafka
- **Maxwell**：简单场景，只需要 JSON 输出

---

## 常见问题

### 1. Canal 延迟高怎么办？

**原因：**
- MySQL binlog 写入慢
- Canal 解析慢
- Client 消费慢

**解决方案：**
- 优化 MySQL 性能
- 增加 Canal Server 资源
- 优化 Client 消费逻辑
- 使用批量消费

### 2. 如何保证数据不丢失？

**方案：**
- 使用文件或 ZooKeeper 模式存储 Position
- Client 处理完数据后再 ACK
- 支持断点续传

### 3. 如何处理 DDL 变更？

**方案：**
- Canal 会捕获 DDL 事件
- Client 需要处理 DDL 事件
- 可能需要重建下游系统结构

### 4. 如何过滤敏感数据？

**方案：**
- 使用 filter.regex 过滤表
- 在 Client 端过滤字段
- 使用数据脱敏

### 5. Canal 支持哪些 MySQL 版本？

**支持：**
- MySQL 5.6+
- MySQL 5.7
- MySQL 8.0

**注意：** MySQL 8.0 需要特殊配置

---

## 总结

### Canal 的核心优势

1. **实时性**：基于 binlog，毫秒级延迟
2. **可靠性**：基于 binlog，数据完整
3. **解耦**：数据库和下游系统解耦
4. **灵活性**：支持多种下游系统
5. **易用性**：配置简单，易于部署

### 适用场景

- **数据同步**：数据库主从同步
- **缓存更新**：自动更新缓存
- **搜索引擎**：同步到 Elasticsearch
- **数据仓库**：实时 ETL
- **消息队列**：数据库变更作为消息
- **监控审计**：数据变更追踪

### 学习建议

1. **理解 Binlog**：掌握 MySQL binlog 基础知识
2. **实践部署**：动手部署 Canal Server
3. **编写 Client**：编写简单的 Canal Client
4. **生产优化**：学习生产环境的优化配置

### 进一步学习

- **官方文档**：https://github.com/alibaba/canal/wiki
- **源码阅读**：理解 Canal 的实现原理
- **生产实践**：学习生产环境的部署和运维

Canal 是数据库变更数据捕获的优秀工具，掌握它有助于构建实时数据同步系统。

---

## 参考资料

- [Canal GitHub](https://github.com/alibaba/canal)
- [Canal 官方文档](https://github.com/alibaba/canal/wiki)
- [MySQL Binlog 文档](https://dev.mysql.com/doc/refman/8.0/en/binary-log.html)
- [CDC 技术对比](https://debezium.io/blog/2018/07/16/debezium-0-9-0-final-released/)

