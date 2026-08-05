---
title: "MySQL 面试题"
date: 2025-12-26
main: "数据库"
sub: ["mysql"]
summary: "MySQL 面试题整理，涵盖基础到高级的各个方面，包括 SQL、索引、事务、存储引擎、性能优化、主从复制等"
---

# MySQL 面试题

## 目录

- [基础概念](#基础概念)
- [SQL 基础](#sql-基础)
- [索引详解](#索引详解)
- [事务与锁](#事务与锁)
- [存储引擎](#存储引擎)
- [性能优化](#性能优化)
- [主从复制](#主从复制)
- [分库分表](#分库分表)
- [常见问题与解决方案](#常见问题与解决方案)
- [高级特性](#高级特性)

---

## 基础概念

### 1. 什么是 MySQL？它有哪些特点？

**答案：**
MySQL 是一个开源的关系型数据库管理系统（RDBMS），使用 SQL 语言进行数据库管理。

**主要特点：**
- **开源免费**：遵循 GPL 协议
- **跨平台**：支持 Windows、Linux、macOS 等
- **高性能**：优化的查询引擎，支持高并发
- **可扩展**：支持主从复制、集群等
- **多存储引擎**：InnoDB、MyISAM、Memory 等
- **丰富的功能**：事务、视图、存储过程、触发器

### 2. MySQL 的架构是什么？

**答案：**
MySQL 采用分层架构：

```
客户端
  ↓
连接层（Connection Layer）
  ├─ 连接管理
  ├─ 身份验证
  └─ 权限检查
  ↓
服务层（Server Layer）
  ├─ SQL 接口
  ├─ 解析器（Parser）
  ├─ 优化器（Optimizer）
  ├─ 查询缓存
  └─ 执行器
  ↓
存储引擎层（Storage Engine Layer）
  ├─ InnoDB
  ├─ MyISAM
  └─ Memory
  ↓
文件系统（File System）
```

**各层功能：**
- **连接层**：管理客户端连接，处理认证和权限
- **服务层**：SQL 解析、优化、执行
- **存储引擎层**：数据存储和检索
- **文件系统**：物理存储

### 3. MySQL 有哪些存储引擎？如何选择？

**答案：**

| 存储引擎 | 事务支持 | 外键 | 锁粒度 | 适用场景 |
|---------|---------|------|--------|---------|
| **InnoDB** | ✅ | ✅ | 行锁 | 事务处理、高并发 |
| **MyISAM** | ❌ | ❌ | 表锁 | 读多写少、全文索引 |
| **Memory** | ❌ | ❌ | 表锁 | 临时表、缓存 |
| **Archive** | ❌ | ❌ | 行锁 | 归档数据 |
| **CSV** | ❌ | ❌ | 表锁 | 数据导入导出 |

**选择建议：**
- **InnoDB**：默认选择，支持事务和外键，适合大多数场景
- **MyISAM**：读多写少，不需要事务的场景
- **Memory**：临时表、缓存数据

### 4. MySQL 的数据类型有哪些？

**答案：**

**1. 整数类型**
- `TINYINT`：1 字节（-128 到 127）
- `SMALLINT`：2 字节
- `MEDIUMINT`：3 字节
- `INT`：4 字节
- `BIGINT`：8 字节

**2. 浮点类型**
- `FLOAT`：单精度浮点数
- `DOUBLE`：双精度浮点数
- `DECIMAL`：精确小数（推荐用于金额）

**3. 字符串类型**
- `CHAR`：固定长度（0-255）
- `VARCHAR`：可变长度（0-65535）
- `TEXT`：长文本
- `BLOB`：二进制大对象

**4. 日期时间类型**
- `DATE`：日期（YYYY-MM-DD）
- `TIME`：时间（HH:MM:SS）
- `DATETIME`：日期时间
- `TIMESTAMP`：时间戳（自动更新）

**5. 其他类型**
- `ENUM`：枚举
- `SET`：集合
- `JSON`：JSON 数据（MySQL 5.7+）

### 5. CHAR 和 VARCHAR 的区别？

**答案：**

| 特性 | CHAR | VARCHAR |
|------|------|---------|
| **长度** | 固定长度 | 可变长度 |
| **存储** | 固定分配空间 | 按实际长度存储 |
| **效率** | 查询效率高 | 存储效率高 |
| **适用场景** | 固定长度数据（如手机号） | 可变长度数据（如姓名） |

**示例：**
```sql
-- CHAR：固定 10 字节，存储 "abc" 也占用 10 字节
CHAR(10)  -- "abc       "（7 个空格）

-- VARCHAR：可变长度，存储 "abc" 只占用 3 字节 + 1 字节长度标识
VARCHAR(10)  -- "abc"（3 字节）
```

**选择建议：**
- **CHAR**：固定长度数据（如身份证号、手机号）
- **VARCHAR**：可变长度数据（如姓名、地址）

---

## SQL 基础

### 6. SQL 语句有哪些类型？

**答案：**

**1. DDL（Data Definition Language）数据定义语言**
- `CREATE`：创建数据库、表、索引等
- `ALTER`：修改表结构
- `DROP`：删除数据库、表等
- `TRUNCATE`：清空表数据

**2. DML（Data Manipulation Language）数据操作语言**
- `INSERT`：插入数据
- `UPDATE`：更新数据
- `DELETE`：删除数据

**3. DQL（Data Query Language）数据查询语言**
- `SELECT`：查询数据

**4. DCL（Data Control Language）数据控制语言**
- `GRANT`：授予权限
- `REVOKE`：撤销权限

**5. TCL（Transaction Control Language）事务控制语言**
- `COMMIT`：提交事务
- `ROLLBACK`：回滚事务
- `SAVEPOINT`：保存点

### 7. JOIN 的类型有哪些？

**答案：**

**1. INNER JOIN（内连接）**
- 返回两个表中匹配的行
```sql
SELECT * FROM A INNER JOIN B ON A.id = B.id;
```

**2. LEFT JOIN（左连接）**
- 返回左表所有行，右表匹配的行
```sql
SELECT * FROM A LEFT JOIN B ON A.id = B.id;
```

**3. RIGHT JOIN（右连接）**
- 返回右表所有行，左表匹配的行
```sql
SELECT * FROM A RIGHT JOIN B ON A.id = B.id;
```

**4. FULL OUTER JOIN（全外连接）**
- MySQL 不支持，可用 UNION 实现
```sql
SELECT * FROM A LEFT JOIN B ON A.id = B.id
UNION
SELECT * FROM A RIGHT JOIN B ON A.id = B.id;
```

**5. CROSS JOIN（交叉连接）**
- 返回两个表的笛卡尔积
```sql
SELECT * FROM A CROSS JOIN B;
```

### 8. UNION 和 UNION ALL 的区别？

**答案：**

| 特性 | UNION | UNION ALL |
|------|-------|-----------|
| **去重** | 自动去重 | 不去重 |
| **性能** | 较慢（需要排序去重） | 较快 |
| **排序** | 结果排序 | 结果不排序 |

**示例：**
```sql
-- UNION：去重
SELECT name FROM table1
UNION
SELECT name FROM table2;

-- UNION ALL：不去重
SELECT name FROM table1
UNION ALL
SELECT name FROM table2;
```

**选择建议：**
- 需要去重：使用 `UNION`
- 不需要去重：使用 `UNION ALL`（性能更好）

### 9. 子查询有哪些类型？

**答案：**

**1. 标量子查询（Scalar Subquery）**
- 返回单个值
```sql
SELECT * FROM users WHERE age > (SELECT AVG(age) FROM users);
```

**2. 行子查询（Row Subquery）**
- 返回一行多列
```sql
SELECT * FROM users WHERE (name, age) = (SELECT name, age FROM admins LIMIT 1);
```

**3. 列子查询（Column Subquery）**
- 返回一列多行
```sql
SELECT * FROM users WHERE id IN (SELECT user_id FROM orders);
```

**4. 表子查询（Table Subquery）**
- 返回多行多列
```sql
SELECT * FROM (SELECT id, name FROM users WHERE age > 18) AS adults;
```

**5. EXISTS 子查询**
- 检查是否存在
```sql
SELECT * FROM users WHERE EXISTS (SELECT 1 FROM orders WHERE orders.user_id = users.id);
```

### 10. GROUP BY 和 HAVING 的区别？

**答案：**

**GROUP BY：**
- 对结果集进行分组
- 通常与聚合函数一起使用
- 在 WHERE 之后执行

**HAVING：**
- 对分组后的结果进行过滤
- 只能用于 GROUP BY 之后
- 可以使用聚合函数

**示例：**
```sql
-- 按部门分组，统计每个部门的平均工资，只显示平均工资 > 5000 的部门
SELECT department, AVG(salary) as avg_salary
FROM employees
WHERE status = 'active'  -- WHERE 过滤原始数据
GROUP BY department
HAVING AVG(salary) > 5000;  -- HAVING 过滤分组后的数据
```

**执行顺序：**
```
FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT
```

---

## 索引详解

### 11. 什么是索引？索引的作用是什么？

**答案：**
索引是数据库中用于快速查找数据的数据结构，类似于书籍的目录。

**作用：**
- **加速查询**：大幅提高查询速度
- **唯一约束**：唯一索引保证数据唯一性
- **排序优化**：索引可以帮助排序操作

**代价：**
- **存储空间**：索引需要额外的存储空间
- **维护成本**：插入、更新、删除需要维护索引
- **创建时间**：大表创建索引需要时间

### 12. MySQL 索引有哪些类型？

**答案：**

**1. 按数据结构分类**
- **B+Tree 索引**：默认索引类型，适合范围查询
- **Hash 索引**：Memory 引擎支持，等值查询快
- **Full-Text 索引**：全文索引，用于文本搜索
- **R-Tree 索引**：空间索引，用于地理数据

**2. 按功能分类**
- **普通索引（INDEX）**：最基本的索引
- **唯一索引（UNIQUE）**：值必须唯一
- **主键索引（PRIMARY KEY）**：主键，唯一且非空
- **全文索引（FULLTEXT）**：全文搜索

**3. 按字段数量分类**
- **单列索引**：单个字段
- **组合索引**：多个字段

**创建示例：**
```sql
-- 普通索引
CREATE INDEX idx_name ON users(name);

-- 唯一索引
CREATE UNIQUE INDEX idx_email ON users(email);

-- 组合索引
CREATE INDEX idx_name_age ON users(name, age);

-- 全文索引
CREATE FULLTEXT INDEX idx_content ON articles(content);
```

### 13. B+Tree 索引的原理是什么？

**答案：**
B+Tree 是 MySQL InnoDB 引擎默认的索引数据结构。

**B+Tree 特点：**
- **多路平衡树**：每个节点可以有多个子节点
- **所有数据在叶子节点**：非叶子节点只存储索引键
- **叶子节点有序链表**：便于范围查询
- **树高较低**：减少磁盘 I/O 次数

**结构示例：**
```
         [50]
        /    \
    [20, 30]  [70, 80]
    /  |  \    /  |  \
[10][25][40] [60][75][90]
```

**查找过程：**
1. 从根节点开始
2. 比较键值，决定走哪个分支
3. 重复直到叶子节点
4. 在叶子节点中找到数据

**优势：**
- **范围查询**：叶子节点有序链表，范围查询高效
- **磁盘友好**：减少磁盘 I/O 次数
- **适合大数据量**：树高低，查询稳定

### 14. 什么是聚簇索引和非聚簇索引？

**答案：**

**聚簇索引（Clustered Index）：**
- 索引和数据存储在一起
- InnoDB 的主键索引就是聚簇索引
- 一个表只有一个聚簇索引
- 数据按索引顺序存储

**非聚簇索引（Non-Clustered Index）：**
- 索引和数据分离存储
- 索引存储的是数据的指针
- 一个表可以有多个非聚簇索引
- 需要回表查询

**对比：**

| 特性 | 聚簇索引 | 非聚簇索引 |
|------|---------|-----------|
| **数据存储** | 索引和数据在一起 | 索引和数据分离 |
| **数量** | 一个表只有一个 | 可以有多个 |
| **查询效率** | 高（无需回表） | 较低（需要回表） |
| **更新代价** | 高（需要移动数据） | 低（只需更新索引） |

**InnoDB 示例：**
```sql
-- 主键索引（聚簇索引）
CREATE TABLE users (
    id INT PRIMARY KEY,  -- 聚簇索引
    name VARCHAR(50),
    email VARCHAR(100),
    INDEX idx_email(email)  -- 非聚簇索引
);
```

### 15. 什么是覆盖索引？

**答案：**
覆盖索引（Covering Index）是指查询所需的所有数据都在索引中，无需回表查询。

**示例：**
```sql
-- 表结构
CREATE TABLE users (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    email VARCHAR(100),
    age INT,
    INDEX idx_name_age(name, age)  -- 组合索引
);

-- 覆盖索引查询：所需字段都在索引中
SELECT name, age FROM users WHERE name = 'John';
-- 不需要回表，直接从索引获取数据

-- 非覆盖索引查询：需要回表
SELECT name, email FROM users WHERE name = 'John';
-- 需要回表获取 email 字段
```

**优势：**
- **减少 I/O**：不需要回表，减少磁盘 I/O
- **提高性能**：查询速度更快
- **减少内存**：不需要加载整行数据

**设计原则：**
- 将查询中常用的字段放在索引中
- 使用组合索引覆盖多个查询场景

### 16. 最左前缀原则是什么？

**答案：**
最左前缀原则（Leftmost Prefix Rule）是指组合索引的使用必须从最左边的列开始，不能跳过中间的列。

**示例：**
```sql
-- 创建组合索引
CREATE INDEX idx_name_age_city ON users(name, age, city);

-- ✅ 可以使用索引
SELECT * FROM users WHERE name = 'John';
SELECT * FROM users WHERE name = 'John' AND age = 25;
SELECT * FROM users WHERE name = 'John' AND age = 25 AND city = 'Beijing';

-- ❌ 不能使用索引（跳过了 name）
SELECT * FROM users WHERE age = 25;
SELECT * FROM users WHERE city = 'Beijing';

-- ⚠️ 部分使用索引（只用到 name）
SELECT * FROM users WHERE name = 'John' AND city = 'Beijing';
```

**原理：**
- 组合索引按字段顺序建立 B+Tree
- 先按第一个字段排序，再按第二个字段排序
- 跳过前面的字段无法利用索引

**优化建议：**
- 将选择性高的字段放在前面
- 考虑查询频率和字段顺序

### 17. 索引失效的情况有哪些？

**答案：**

**1. 使用函数或表达式**
```sql
-- ❌ 索引失效
SELECT * FROM users WHERE UPPER(name) = 'JOHN';
SELECT * FROM users WHERE age + 1 = 26;

-- ✅ 可以使用索引
SELECT * FROM users WHERE name = 'JOHN';
SELECT * FROM users WHERE age = 25;
```

**2. 类型转换**
```sql
-- ❌ 索引失效（字符串转数字）
SELECT * FROM users WHERE id = '123';

-- ✅ 可以使用索引
SELECT * FROM users WHERE id = 123;
```

**3. 前导模糊查询**
```sql
-- ❌ 索引失效
SELECT * FROM users WHERE name LIKE '%John';

-- ✅ 可以使用索引
SELECT * FROM users WHERE name LIKE 'John%';
```

**4. OR 条件**
```sql
-- ❌ 索引失效（如果 age 没有索引）
SELECT * FROM users WHERE name = 'John' OR age = 25;

-- ✅ 可以使用索引
SELECT * FROM users WHERE name = 'John' AND age = 25;
```

**5. 不等于操作**
```sql
-- ❌ 索引失效
SELECT * FROM users WHERE name != 'John';
SELECT * FROM users WHERE name <> 'John';

-- ✅ 可以使用索引
SELECT * FROM users WHERE name = 'John';
```

**6. IS NULL / IS NOT NULL**
```sql
-- ❌ 索引失效（取决于数据分布）
SELECT * FROM users WHERE name IS NULL;
```

**7. 组合索引不遵循最左前缀**
```sql
-- 索引：idx_name_age
-- ❌ 索引失效
SELECT * FROM users WHERE age = 25;
```

### 18. 如何优化索引？

**答案：**

**1. 选择合适的字段**
- 选择性高的字段（区分度高）
- 经常用于 WHERE、JOIN、ORDER BY 的字段
- 避免在低选择性字段上建索引（如性别、状态）

**2. 避免过多索引**
- 索引会降低写入性能
- 维护索引需要额外开销
- 一般建议单表索引不超过 5 个

**3. 使用组合索引**
- 覆盖多个查询场景
- 遵循最左前缀原则
- 将选择性高的字段放在前面

**4. 定期分析索引使用情况**
```sql
-- 查看索引使用情况
SHOW INDEX FROM users;

-- 分析查询计划
EXPLAIN SELECT * FROM users WHERE name = 'John';
```

**5. 删除未使用的索引**
```sql
-- 删除索引
DROP INDEX idx_unused ON users;
```

---

## 事务与锁

### 19. 什么是事务？ACID 特性是什么？

**答案：**
事务（Transaction）是一组 SQL 操作的逻辑单元，要么全部成功，要么全部失败。

**ACID 特性：**

**1. 原子性（Atomicity）**
- 事务中的所有操作要么全部成功，要么全部失败
- 通过 undo log 实现

**2. 一致性（Consistency）**
- 事务执行前后，数据库保持一致状态
- 通过约束、触发器保证

**3. 隔离性（Isolation）**
- 并发事务之间相互隔离
- 通过锁机制实现

**4. 持久性（Durability）**
- 事务提交后，数据永久保存
- 通过 redo log 实现

**示例：**
```sql
START TRANSACTION;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;  -- 提交事务
-- 或
ROLLBACK;  -- 回滚事务
```

### 20. MySQL 的隔离级别有哪些？

**答案：**

MySQL 支持四种隔离级别：

**1. READ UNCOMMITTED（读未提交）**
- 最低隔离级别
- 可能读到未提交的数据（脏读）
- 性能最好，但数据不安全

**2. READ COMMITTED（读已提交）**
- 只能读到已提交的数据
- 避免脏读，但可能出现不可重复读
- Oracle 默认级别

**3. REPEATABLE READ（可重复读）**
- 同一事务中多次读取结果一致
- 避免脏读和不可重复读，但可能出现幻读
- **MySQL InnoDB 默认级别**

**4. SERIALIZABLE（串行化）**
- 最高隔离级别
- 完全隔离，避免所有并发问题
- 性能最差

**并发问题：**

| 隔离级别 | 脏读 | 不可重复读 | 幻读 |
|---------|------|-----------|------|
| READ UNCOMMITTED | ✅ | ✅ | ✅ |
| READ COMMITTED | ❌ | ✅ | ✅ |
| REPEATABLE READ | ❌ | ❌ | ✅ |
| SERIALIZABLE | ❌ | ❌ | ❌ |

**设置隔离级别：**
```sql
-- 查看当前隔离级别
SELECT @@transaction_isolation;

-- 设置隔离级别
SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;
```

### 21. 什么是脏读、不可重复读、幻读？

**答案：**

**1. 脏读（Dirty Read）**
- 读取到未提交的数据
- 如果事务回滚，读到的数据就是错误的

**示例：**
```
事务 A：UPDATE users SET balance = 1000 WHERE id = 1;  -- 未提交
事务 B：SELECT balance FROM users WHERE id = 1;  -- 读到 1000（脏读）
事务 A：ROLLBACK;  -- 回滚
事务 B：读到的数据是错误的
```

**2. 不可重复读（Non-Repeatable Read）**
- 同一事务中多次读取同一数据，结果不一致
- 由于其他事务修改了数据

**示例：**
```
事务 A：SELECT balance FROM users WHERE id = 1;  -- 读到 100
事务 B：UPDATE users SET balance = 200 WHERE id = 1; COMMIT;
事务 A：SELECT balance FROM users WHERE id = 1;  -- 读到 200（不一致）
```

**3. 幻读（Phantom Read）**
- 同一事务中多次查询，结果集不一致
- 由于其他事务插入了新数据

**示例：**
```
事务 A：SELECT * FROM users WHERE age > 18;  -- 返回 10 条
事务 B：INSERT INTO users VALUES (11, 'John', 20); COMMIT;
事务 A：SELECT * FROM users WHERE age > 18;  -- 返回 11 条（幻读）
```

**InnoDB 的解决方案：**
- **MVCC（多版本并发控制）**：解决不可重复读
- **Next-Key Lock**：解决幻读

### 22. MySQL 的锁有哪些类型？

**答案：**

**1. 按锁的粒度分类**

**表锁（Table Lock）：**
- 锁定整个表
- MyISAM 默认锁类型
- 开销小，加锁快，但并发度低

**行锁（Row Lock）：**
- 锁定单行数据
- InnoDB 默认锁类型
- 开销大，加锁慢，但并发度高

**页锁（Page Lock）：**
- 锁定一页数据
- 介于表锁和行锁之间

**2. 按锁的类型分类**

**共享锁（Shared Lock / S Lock）：**
- 读锁，多个事务可以同时持有
- `SELECT ... LOCK IN SHARE MODE`

**排他锁（Exclusive Lock / X Lock）：**
- 写锁，只有一个事务可以持有
- `SELECT ... FOR UPDATE`、`INSERT`、`UPDATE`、`DELETE`

**3. 按锁的意图分类**

**意向共享锁（IS Lock）：**
- 表示事务想要在表上获取共享锁

**意向排他锁（IX Lock）：**
- 表示事务想要在表上获取排他锁

**锁的兼容性：**

|      | S  | X  | IS | IX |
|------|----|----|----|----|
| **S**  | ✅ | ❌ | ✅ | ❌ |
| **X**  | ❌ | ❌ | ❌ | ❌ |
| **IS** | ✅ | ❌ | ✅ | ✅ |
| **IX** | ❌ | ❌ | ✅ | ✅ |

### 23. InnoDB 的行锁是如何实现的？

**答案：**
InnoDB 的行锁通过索引实现，如果没有索引，会退化为表锁。

**实现方式：**

**1. Record Lock（记录锁）**
- 锁定单行记录
- 在索引记录上加锁

**2. Gap Lock（间隙锁）**
- 锁定索引记录之间的间隙
- 防止其他事务在间隙中插入数据
- 解决幻读问题

**3. Next-Key Lock（临键锁）**
- Record Lock + Gap Lock
- 锁定记录和记录前的间隙
- InnoDB 默认的行锁算法

**示例：**
```sql
-- 表：id (1, 3, 5, 7, 9)
-- 查询：WHERE id > 3 AND id < 7

-- Next-Key Lock 锁定：
-- (3, 5] - 记录 5 和间隙 (3, 5)
-- (5, 7) - 间隙 (5, 7)
-- 防止插入 id = 4 或 id = 6 的记录
```

**锁的升级：**
- 如果查询没有使用索引，行锁会升级为表锁
- 因此，WHERE 条件应该使用索引字段

### 24. 什么是死锁？如何避免？

**答案：**
死锁（Deadlock）是指两个或多个事务相互等待对方释放锁，导致无法继续执行。

**死锁示例：**
```
事务 A：
  UPDATE users SET name = 'A' WHERE id = 1;  -- 锁定 id=1
  UPDATE users SET name = 'A' WHERE id = 2;  -- 等待 id=2 的锁

事务 B：
  UPDATE users SET name = 'B' WHERE id = 2;  -- 锁定 id=2
  UPDATE users SET name = 'B' WHERE id = 1;  -- 等待 id=1 的锁

结果：死锁！
```

**避免死锁的方法：**

**1. 按相同顺序访问资源**
```sql
-- ✅ 好：按 id 顺序访问
UPDATE users SET name = 'A' WHERE id = 1;
UPDATE users SET name = 'A' WHERE id = 2;

-- ❌ 差：顺序不一致可能导致死锁
UPDATE users SET name = 'A' WHERE id = 2;
UPDATE users SET name = 'A' WHERE id = 1;
```

**2. 减少事务持有时间**
- 尽快提交事务
- 避免在事务中执行耗时操作

**3. 降低隔离级别**
- 使用较低的隔离级别（如 READ COMMITTED）
- 减少锁的持有时间

**4. 使用索引**
- 确保 WHERE 条件使用索引
- 避免行锁升级为表锁

**5. 死锁检测和处理**
```sql
-- 查看死锁信息
SHOW ENGINE INNODB STATUS;

-- MySQL 会自动检测死锁并回滚一个事务
```

---

## 存储引擎

### 25. InnoDB 和 MyISAM 的区别？

**答案：**

| 特性 | InnoDB | MyISAM |
|------|--------|--------|
| **事务** | ✅ 支持 | ❌ 不支持 |
| **外键** | ✅ 支持 | ❌ 不支持 |
| **锁粒度** | 行锁 | 表锁 |
| **并发性能** | 高 | 低 |
| **崩溃恢复** | 支持 | 不支持 |
| **全文索引** | MySQL 5.6+ 支持 | 支持 |
| **存储文件** | .ibd（数据+索引） | .MYD（数据）+ .MYI（索引） |
| **适用场景** | 事务处理、高并发 | 读多写少、不需要事务 |

**选择建议：**
- **InnoDB**：默认选择，适合大多数场景
- **MyISAM**：读多写少，不需要事务的场景

### 26. InnoDB 的存储结构是什么？

**答案：**
InnoDB 的存储结构包括：

**1. 表空间（Tablespace）**
- **系统表空间**：存储系统元数据、undo log
- **独立表空间**：每个表一个 .ibd 文件（MySQL 5.7+ 默认）

**2. 段（Segment）**
- **数据段**：B+Tree 的叶子节点
- **索引段**：B+Tree 的非叶子节点
- **回滚段**：undo log

**3. 区（Extent）**
- 由连续的页组成
- 每个区 1MB（64 个页）

**4. 页（Page）**
- 最小的存储单位
- 每个页 16KB
- 存储数据行和索引

**5. 行（Row）**
- 实际的数据记录
- 行格式：Compact、Redundant、Dynamic、Compressed

**存储文件：**
```
数据库目录/
  ├─ db.opt（数据库配置）
  ├─ users.frm（表结构）
  └─ users.ibd（InnoDB 数据和索引）
```

### 27. InnoDB 的日志文件有哪些？

**答案：**

**1. Redo Log（重做日志）**
- 记录事务的修改操作
- 用于崩溃恢复
- 文件：`ib_logfile0`、`ib_logfile1`
- 循环写入，大小固定

**2. Undo Log（回滚日志）**
- 记录事务修改前的数据
- 用于事务回滚和 MVCC
- 存储在系统表空间或独立表空间

**3. Binlog（二进制日志）**
- 记录所有 DDL 和 DML 操作
- 用于主从复制和数据恢复
- 文件：`mysql-bin.000001`、`mysql-bin.000002` 等

**日志的作用：**

**Redo Log：**
- 保证事务的持久性
- 崩溃后恢复未提交的事务

**Undo Log：**
- 支持事务回滚
- 实现 MVCC（多版本并发控制）

**Binlog：**
- 主从复制
- 数据恢复
- 审计

### 28. 什么是 WAL（Write-Ahead Logging）？InnoDB 如何实现 WAL？

**答案：**
WAL（Write-Ahead Logging，预写式日志）是一种数据持久化技术，要求所有数据修改必须先写入日志，然后才能写入数据文件。

**WAL 的核心原则：**
> **先写日志，后写数据**（Log First, Data Second）

**InnoDB 的 WAL 实现：**

**1. Redo Log 作为 WAL**
- InnoDB 使用 Redo Log 实现 WAL 机制
- 所有数据修改先写入 Redo Log
- 然后才写入数据页（Buffer Pool）

**2. 工作流程：**

```
事务执行
  ↓
修改 Buffer Pool 中的数据页（内存）
  ↓
写入 Redo Log Buffer（内存）
  ↓
根据配置刷盘策略，将 Redo Log 写入磁盘
  ↓
事务提交时，确保 Redo Log 已落盘
  ↓
数据页异步刷盘（Checkpoint）
```

**3. 刷盘策略（innodb_flush_log_at_trx_commit）：**

**策略 0：**
```ini
innodb_flush_log_at_trx_commit = 0
```
- 每秒将 Redo Log Buffer 写入磁盘并刷新
- 事务提交时不强制刷盘
- **性能最好，但可能丢失最多 1 秒的数据**

**策略 1（默认）：**
```ini
innodb_flush_log_at_trx_commit = 1
```
- 每次事务提交都将 Redo Log Buffer 写入磁盘并刷新
- **最安全，保证数据不丢失**
- 性能相对较低

**策略 2：**
```ini
innodb_flush_log_at_trx_commit = 2
```
- 每次事务提交都将 Redo Log Buffer 写入磁盘，但不刷新
- 每秒刷新一次
- **性能较好，但崩溃可能丢失最多 1 秒的数据**

**4. Checkpoint（检查点）机制：**

**作用：**
- 将脏页（Dirty Page）从 Buffer Pool 刷新到磁盘
- 标记 Redo Log 中已持久化的位置
- 回收 Redo Log 空间

**触发条件：**
- Redo Log 空间不足
- 达到检查点时间间隔（`innodb_checkpoint_timeout`）
- 缓冲池脏页比例过高（`innodb_max_dirty_pages_pct`）

**Checkpoint 类型：**
- **Sharp Checkpoint**：关闭数据库时，刷新所有脏页
- **Fuzzy Checkpoint**：运行时，只刷新部分脏页

**5. WAL 的优势：**

**1. 性能提升**
- **顺序写入**：Redo Log 是顺序写入，比随机写入快很多
- **批量刷新**：数据页可以批量刷新，减少 I/O 次数
- **减少磁盘 I/O**：不需要每次修改都写磁盘

**2. 数据安全**
- **崩溃恢复**：通过 Redo Log 可以恢复未提交的事务
- **持久性保证**：事务提交时 Redo Log 已落盘，保证数据不丢失

**3. 并发性能**
- **减少锁竞争**：数据页在内存中修改，不需要立即写磁盘
- **提高吞吐量**：批量处理提高整体性能

**6. Redo Log 的循环写入：**

**结构：**
```
Redo Log 文件组（通常 2 个文件）
  ├─ ib_logfile0 (256MB)
  └─ ib_logfile1 (256MB)

写入位置（Write Pos）→ 循环写入
检查点位置（Checkpoint）→ 标记已刷新位置
```

**工作方式：**
- Redo Log 是循环写入的
- Write Pos 向前移动，写入新的日志
- Checkpoint 向前移动，标记已刷新的位置
- 当 Write Pos 追上 Checkpoint 时，需要等待 Checkpoint 推进

**7. 崩溃恢复过程：**

```
数据库启动
  ↓
读取 Redo Log
  ↓
找到 Checkpoint 位置
  ↓
从 Checkpoint 开始重放 Redo Log
  ↓
恢复未提交的事务（Rollback）
  ↓
恢复已提交但未刷盘的数据（Redo）
  ↓
数据库恢复完成
```

**8. WAL 与 Binlog 的区别：**

| 特性 | Redo Log (WAL) | Binlog |
|------|---------------|--------|
| **作用** | 保证事务持久性 | 主从复制、数据恢复 |
| **存储引擎** | InnoDB 特有 | MySQL Server 层 |
| **记录内容** | 物理日志（页的修改） | 逻辑日志（SQL 语句） |
| **写入时机** | 事务执行时 | 事务提交时 |
| **用途** | 崩溃恢复 | 主从复制、时间点恢复 |

**9. 两阶段提交（2PC）：**

为了保证 Redo Log 和 Binlog 的一致性，InnoDB 使用两阶段提交：

**阶段 1（Prepare）：**
- 写入 Redo Log，标记为 Prepare 状态
- 事务可以提交

**阶段 2（Commit）：**
- 写入 Binlog
- 提交 Redo Log（标记为 Commit 状态）

**崩溃恢复：**
- 如果 Redo Log 是 Prepare 状态，检查 Binlog
- 如果 Binlog 完整，提交事务（Redo）
- 如果 Binlog 不完整，回滚事务（Undo）

**10. WAL 配置优化：**

```ini
# Redo Log 文件大小（建议 256MB - 2GB）
innodb_log_file_size = 256M

# Redo Log 文件数量（通常 2 个）
innodb_log_files_in_group = 2

# 刷盘策略（1 = 最安全，0 = 最快）
innodb_flush_log_at_trx_commit = 1

# Redo Log Buffer 大小
innodb_log_buffer_size = 16M

# Checkpoint 相关
innodb_checkpoint_timeout = 60
innodb_max_dirty_pages_pct = 75
```

**总结：**
WAL 是 InnoDB 实现高性能和数据安全的核心机制。通过先写日志后写数据，既保证了数据持久性，又提高了写入性能。理解 WAL 机制对于优化 MySQL 性能和保证数据安全至关重要。

### 29. MVCC 是什么？如何实现的？

**答案：**
MVCC（Multi-Version Concurrency Control，多版本并发控制）是 InnoDB 实现高并发的重要机制。

**原理：**
- 为每行数据维护多个版本
- 读操作读取历史版本，不阻塞写操作
- 写操作创建新版本

**实现机制：**

**1. 隐藏字段**
- `DB_TRX_ID`：事务 ID，记录创建/修改该行的事务 ID
- `DB_ROLL_PTR`：回滚指针，指向 undo log 中的历史版本

**2. Read View（读视图）**
- 事务开始时的快照
- 包含：活跃事务列表、最小事务 ID、最大事务 ID

**3. 版本链**
- 通过 undo log 构建版本链
- 根据 Read View 判断可见性

**判断规则：**
- 如果 `DB_TRX_ID < min_trx_id`：可见（已提交）
- 如果 `DB_TRX_ID > max_trx_id`：不可见（未来事务）
- 如果 `min_trx_id <= DB_TRX_ID <= max_trx_id`：
  - 在活跃事务列表中：不可见（未提交）
  - 不在活跃事务列表中：可见（已提交）

**优势：**
- **读不阻塞写**：读操作读取历史版本
- **写不阻塞读**：写操作创建新版本
- **提高并发性能**：减少锁竞争

---

## 性能优化

### 30. 如何优化 SQL 查询？

**答案：**

**1. 使用索引**
```sql
-- ✅ 使用索引
SELECT * FROM users WHERE id = 1;

-- ❌ 不使用索引
SELECT * FROM users WHERE UPPER(name) = 'JOHN';
```

**2. 避免 SELECT ***
```sql
-- ❌ 差：查询所有字段
SELECT * FROM users;

-- ✅ 好：只查询需要的字段
SELECT id, name FROM users;
```

**3. 使用 LIMIT**
```sql
-- ✅ 限制返回数量
SELECT * FROM users LIMIT 10;
```

**4. 避免子查询，使用 JOIN**
```sql
-- ❌ 差：子查询
SELECT * FROM users WHERE id IN (SELECT user_id FROM orders);

-- ✅ 好：JOIN
SELECT u.* FROM users u INNER JOIN orders o ON u.id = o.user_id;
```

**5. 使用 EXISTS 代替 IN**
```sql
-- ✅ EXISTS 通常比 IN 性能好
SELECT * FROM users WHERE EXISTS (
    SELECT 1 FROM orders WHERE orders.user_id = users.id
);
```

**6. 避免在 WHERE 子句中使用函数**
```sql
-- ❌ 差：使用函数
SELECT * FROM users WHERE DATE(created_at) = '2024-01-01';

-- ✅ 好：使用范围查询
SELECT * FROM users WHERE created_at >= '2024-01-01' AND created_at < '2024-01-02';
```

**7. 使用 UNION ALL 代替 UNION**
```sql
-- ✅ UNION ALL 不去重，性能更好
SELECT name FROM table1 UNION ALL SELECT name FROM table2;
```

### 31. EXPLAIN 如何分析查询计划？

**答案：**
`EXPLAIN` 用于分析 SQL 查询的执行计划。

**使用方法：**
```sql
EXPLAIN SELECT * FROM users WHERE name = 'John';
```

**关键字段：**

**1. type（访问类型）**
- `ALL`：全表扫描（最差）
- `index`：全索引扫描
- `range`：范围扫描
- `ref`：非唯一索引扫描
- `eq_ref`：唯一索引扫描
- `const`：常量查询（最好）

**2. key（使用的索引）**
- 显示实际使用的索引
- `NULL` 表示未使用索引

**3. rows（扫描行数）**
- 预估扫描的行数
- 越小越好

**4. Extra（额外信息）**
- `Using index`：覆盖索引
- `Using where`：使用 WHERE 过滤
- `Using filesort`：需要排序
- `Using temporary`：使用临时表

**优化示例：**
```sql
-- 优化前：全表扫描
EXPLAIN SELECT * FROM users WHERE name = 'John';
-- type: ALL, rows: 10000

-- 优化后：使用索引
CREATE INDEX idx_name ON users(name);
EXPLAIN SELECT * FROM users WHERE name = 'John';
-- type: ref, key: idx_name, rows: 10
```

### 32. 如何优化慢查询？

**答案：**

**1. 开启慢查询日志**
```sql
-- 开启慢查询日志
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;  -- 超过 2 秒的查询记录

-- 查看慢查询日志
SHOW VARIABLES LIKE 'slow_query_log%';
```

**2. 分析慢查询**
```sql
-- 使用 mysqldumpslow 分析
mysqldumpslow -s t -t 10 /var/log/mysql/slow.log

-- 使用 pt-query-digest（Percona Toolkit）
pt-query-digest /var/log/mysql/slow.log
```

**3. 优化方法**
- **添加索引**：为 WHERE、JOIN、ORDER BY 字段添加索引
- **优化 SQL**：重写查询，避免全表扫描
- **分页优化**：使用游标分页代替 OFFSET
- **缓存**：使用 Redis 缓存热点数据

**4. 分页优化**
```sql
-- ❌ 差：OFFSET 越大越慢
SELECT * FROM users LIMIT 10000, 20;

-- ✅ 好：使用游标分页
SELECT * FROM users WHERE id > 10000 LIMIT 20;
```

### 33. 如何优化 JOIN 查询？

**答案：**

**1. 使用索引**
```sql
-- ✅ 为 JOIN 字段添加索引
CREATE INDEX idx_user_id ON orders(user_id);
SELECT * FROM users u JOIN orders o ON u.id = o.user_id;
```

**2. 小表驱动大表**
```sql
-- ✅ 小表在前（驱动表）
SELECT * FROM small_table s JOIN large_table l ON s.id = l.id;

-- ❌ 大表在前
SELECT * FROM large_table l JOIN small_table s ON l.id = s.id;
```

**3. 避免多表 JOIN**
- 超过 3 个表的 JOIN 性能较差
- 考虑拆分为多个查询

**4. 使用 EXISTS 代替 JOIN**
```sql
-- ✅ EXISTS 可能比 JOIN 性能好
SELECT * FROM users WHERE EXISTS (
    SELECT 1 FROM orders WHERE orders.user_id = users.id
);
```

### 34. MySQL 的配置优化有哪些？

**答案：**

**1. 连接相关**
```ini
# 最大连接数
max_connections = 1000

# 连接超时
wait_timeout = 600
interactive_timeout = 600
```

**2. 缓冲池（InnoDB）**
```ini
# InnoDB 缓冲池大小（建议为内存的 70-80%）
innodb_buffer_pool_size = 4G

# 缓冲池实例数
innodb_buffer_pool_instances = 4
```

**3. 日志相关**
```ini
# Redo Log 大小
innodb_log_file_size = 256M
innodb_log_files_in_group = 2

# Binlog 格式
binlog_format = ROW

# Binlog 过期时间
expire_logs_days = 7
```

**4. 查询缓存（MySQL 5.7 及之前）**
```ini
# 查询缓存大小
query_cache_size = 64M
query_cache_type = 1
```

**注意：** MySQL 8.0 已移除查询缓存

**5. 临时表**
```ini
# 临时表大小
tmp_table_size = 64M
max_heap_table_size = 64M
```

---

## 主从复制

### 35. MySQL 主从复制的原理是什么？

**答案：**
主从复制（Master-Slave Replication）是将主库的数据复制到从库的过程。

**复制流程：**

**1. 主库（Master）**
- 执行 SQL 语句，记录到 Binlog
- Binlog Dump 线程读取 Binlog，发送给从库

**2. 从库（Slave）**
- I/O 线程连接主库，接收 Binlog
- 将 Binlog 写入 Relay Log（中继日志）
- SQL 线程读取 Relay Log，执行 SQL 语句

**流程图：**
```
主库（Master）
  ├─ 执行 SQL
  ├─ 写入 Binlog
  └─ Binlog Dump 线程
         ↓（网络传输）
从库（Slave）
  ├─ I/O 线程（接收 Binlog）
  ├─ 写入 Relay Log
  └─ SQL 线程（执行 SQL）
```

**配置示例：**
```ini
# 主库配置（my.cnf）
[mysqld]
server-id = 1
log-bin = mysql-bin
binlog-format = ROW

# 从库配置（my.cnf）
[mysqld]
server-id = 2
relay-log = mysql-relay-bin
read-only = 1
```

**复制方式：**

**1. 异步复制（Asynchronous Replication）**
- 主库提交事务后立即返回
- 不等待从库确认
- 性能最好，但可能丢失数据

**2. 半同步复制（Semi-Synchronous Replication）**
- 主库等待至少一个从库确认
- 平衡性能和安全性
- 需要安装插件

**3. 组复制（Group Replication）**
- MySQL 5.7+ 支持
- 多主复制，自动故障转移

### 36. 主从延迟的原因和解决方案？

**答案：**

**延迟原因：**

**1. 网络延迟**
- 主从库网络延迟高
- 解决方案：使用内网，优化网络

**2. 从库性能不足**
- 从库硬件配置低
- 解决方案：提升从库配置

**3. 大事务**
- 大事务执行时间长
- 解决方案：拆分大事务

**4. 从库负载高**
- 从库承担读请求
- 解决方案：增加从库数量

**5. Binlog 格式**
- Statement 格式可能延迟
- 解决方案：使用 ROW 格式

**解决方案：**

**1. 并行复制**
```ini
# 开启并行复制
slave_parallel_workers = 4
slave_parallel_type = LOGICAL_CLOCK
```

**2. 优化从库配置**
```ini
# 关闭不必要的功能
skip-slave-start = 0
slave-skip-errors = 0
```

**3. 监控延迟**
```sql
-- 查看复制延迟
SHOW SLAVE STATUS\G
-- 关注：Seconds_Behind_Master
```

**4. 使用 MTS（Multi-Threaded Slave）**
- MySQL 5.7+ 支持并行复制
- 提高从库执行速度

---

## 分库分表

### 37. 什么是分库分表？什么时候需要？

**答案：**
分库分表是将大表拆分成多个小表，分散到多个数据库中。

**分库：**
- 将数据分散到多个数据库
- 每个数据库独立运行

**分表：**
- 将大表拆分成多个小表
- 可以分库分表结合使用

**什么时候需要：**

**1. 数据量过大**
- 单表数据超过千万级别
- 查询性能下降

**2. 并发过高**
- 单库无法承受高并发
- 需要分散压力

**3. 存储空间不足**
- 单库存储空间有限
- 需要分散存储

**分表策略：**

**1. 水平分表**
- 按行拆分，表结构相同
- 如：按用户 ID 取模分表

**2. 垂直分表**
- 按列拆分，将字段分散到不同表
- 如：将常用字段和扩展字段分开

**分库分表示例：**
```sql
-- 按用户 ID 分表（4 张表）
users_0  -- id % 4 = 0
users_1  -- id % 4 = 1
users_2  -- id % 4 = 2
users_3  -- id % 4 = 3

-- 查询时需要路由到对应的表
SELECT * FROM users_{id % 4} WHERE id = ?;
```

### 38. 分库分表的优缺点？

**答案：**

**优点：**
- **提高性能**：单表数据量减少，查询更快
- **提高并发**：分散到多个库，提高并发能力
- **扩展性好**：可以水平扩展
- **故障隔离**：单个库故障不影响其他库

**缺点：**
- **复杂度高**：需要处理路由、跨库查询等
- **事务问题**：跨库事务难以保证
- **JOIN 困难**：跨库 JOIN 性能差
- **数据一致性**：需要保证数据一致性

**解决方案：**
- **使用中间件**：MyCAT、ShardingSphere 等
- **应用层路由**：在应用层实现路由逻辑
- **分布式事务**：使用 Seata、TCC 等

---

## 常见问题与解决方案

### 39. 如何解决 MySQL 连接数过多？

**答案：**

**问题原因：**
- 连接未正确关闭
- 连接池配置不合理
- 最大连接数设置过小

**解决方案：**

**1. 检查当前连接数**
```sql
-- 查看当前连接数
SHOW PROCESSLIST;
SHOW STATUS LIKE 'Threads_connected';

-- 查看最大连接数
SHOW VARIABLES LIKE 'max_connections';
```

**2. 优化连接**
```sql
-- 增加最大连接数
SET GLOBAL max_connections = 1000;

-- 优化连接超时
SET GLOBAL wait_timeout = 600;
SET GLOBAL interactive_timeout = 600;
```

**3. 使用连接池**
- 应用层使用连接池（如 HikariCP、Druid）
- 复用连接，减少连接数

**4. 检查慢查询**
- 慢查询可能导致连接长时间占用
- 优化慢查询，减少连接持有时间

### 40. 如何解决 MySQL 内存占用过高？

**答案：**

**内存占用来源：**

**1. InnoDB 缓冲池**
- 最大的内存占用
- 建议设置为内存的 70-80%

**2. 连接缓存**
- 每个连接占用内存
- 减少连接数可以降低内存占用

**3. 临时表**
- 排序、GROUP BY 使用临时表
- 优化查询减少临时表使用

**优化方法：**

**1. 调整缓冲池大小**
```ini
# 根据实际情况调整
innodb_buffer_pool_size = 4G
```

**2. 限制连接数**
```ini
max_connections = 500
```

**3. 优化查询**
- 避免大结果集
- 使用 LIMIT 限制返回数量
- 优化排序和分组

**4. 监控内存使用**
```sql
-- 查看内存使用情况
SHOW VARIABLES LIKE '%buffer%';
SHOW STATUS LIKE '%memory%';
```

### 41. 如何备份和恢复 MySQL 数据库？

**答案：**

**1. mysqldump 备份**
```bash
# 备份单个数据库
mysqldump -u root -p database_name > backup.sql

# 备份所有数据库
mysqldump -u root -p --all-databases > all_backup.sql

# 备份表结构
mysqldump -u root -p --no-data database_name > schema.sql

# 备份数据
mysqldump -u root -p --no-create-info database_name > data.sql
```

**2. 恢复数据**
```bash
# 恢复数据库
mysql -u root -p database_name < backup.sql

# 恢复所有数据库
mysql -u root -p < all_backup.sql
```

**3. 物理备份**
```bash
# 使用 Percona XtraBackup
xtrabackup --backup --target-dir=/backup/
xtrabackup --prepare --target-dir=/backup/
```

**4. 备份策略**
- **全量备份**：每天一次
- **增量备份**：每小时一次
- **Binlog 备份**：实时备份
- **异地备份**：防止单点故障

---

## 高级特性

### 42. MySQL 8.0 的新特性有哪些？

**答案：**

**1. 窗口函数（Window Functions）**
```sql
-- ROW_NUMBER、RANK、DENSE_RANK
SELECT 
    name,
    salary,
    ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) as rank
FROM employees;
```

**2. 通用表表达式（CTE）**
```sql
-- WITH 子句
WITH RECURSIVE cte AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1 FROM cte WHERE n < 10
)
SELECT * FROM cte;
```

**3. JSON 增强**
- 更好的 JSON 支持
- JSON 函数增强

**4. 角色管理**
```sql
-- 创建角色
CREATE ROLE 'developer', 'admin';

-- 授予权限
GRANT SELECT ON database.* TO 'developer';
```

**5. 性能提升**
- 查询缓存移除（已优化）
- 更好的优化器
- 更快的 DDL 操作

### 43. 什么是存储过程？如何使用？

**答案：**
存储过程（Stored Procedure）是一组预编译的 SQL 语句，存储在数据库中。

**创建存储过程：**
```sql
DELIMITER //
CREATE PROCEDURE GetUserById(IN user_id INT)
BEGIN
    SELECT * FROM users WHERE id = user_id;
END //
DELIMITER ;
```

**调用存储过程：**
```sql
CALL GetUserById(1);
```

**优点：**
- **性能好**：预编译，执行效率高
- **减少网络传输**：一次调用执行多条 SQL
- **安全性**：可以控制权限

**缺点：**
- **可移植性差**：不同数据库语法不同
- **调试困难**：不如应用层代码容易调试
- **版本控制困难**：难以版本管理

### 44. 什么是触发器？如何使用？

**答案：**
触发器（Trigger）是在表上定义的特殊存储过程，在特定事件发生时自动执行。

**创建触发器：**
```sql
-- 在插入前触发
CREATE TRIGGER before_insert_user
BEFORE INSERT ON users
FOR EACH ROW
BEGIN
    SET NEW.created_at = NOW();
END;

-- 在更新后触发
CREATE TRIGGER after_update_user
AFTER UPDATE ON users
FOR EACH ROW
BEGIN
    INSERT INTO user_logs(user_id, action, timestamp)
    VALUES (NEW.id, 'UPDATE', NOW());
END;
```

**触发器类型：**
- `BEFORE INSERT`：插入前
- `AFTER INSERT`：插入后
- `BEFORE UPDATE`：更新前
- `AFTER UPDATE`：更新后
- `BEFORE DELETE`：删除前
- `AFTER DELETE`：删除后

**注意事项：**
- 触发器会增加数据库负担
- 调试困难
- 建议在应用层实现业务逻辑

### 45. 什么是视图？如何使用？

**答案：**
视图（View）是基于查询结果的虚拟表，不存储数据。

**创建视图：**
```sql
-- 创建视图
CREATE VIEW user_orders AS
SELECT 
    u.id,
    u.name,
    COUNT(o.id) as order_count,
    SUM(o.amount) as total_amount
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.name;

-- 使用视图
SELECT * FROM user_orders WHERE order_count > 5;
```

**优点：**
- **简化查询**：封装复杂查询
- **安全性**：可以隐藏敏感字段
- **一致性**：统一数据访问接口

**缺点：**
- **性能**：视图查询可能较慢
- **限制**：某些操作不支持（如某些 JOIN）

### 46. MySQL 的字符集和排序规则是什么？

**答案：**

**字符集（Character Set）：**
- 定义字符的编码方式
- 常用字符集：`utf8`、`utf8mb4`、`latin1`

**排序规则（Collation）：**
- 定义字符的排序和比较规则
- 常用排序规则：`utf8mb4_general_ci`、`utf8mb4_unicode_ci`

**utf8 vs utf8mb4：**
- **utf8**：最多 3 字节，不支持 emoji（如 😀）
- **utf8mb4**：最多 4 字节，支持 emoji（推荐）

**设置字符集：**
```sql
-- 数据库级别
CREATE DATABASE db_name CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 表级别
CREATE TABLE users (
    id INT PRIMARY KEY,
    name VARCHAR(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 字段级别
ALTER TABLE users MODIFY name VARCHAR(50) CHARACTER SET utf8mb4;
```

**选择建议：**
- 使用 `utf8mb4` 字符集
- 使用 `utf8mb4_unicode_ci` 排序规则（更准确）

---

## 总结

MySQL 是一个功能强大的关系型数据库，掌握其核心概念、SQL 语法、索引优化、事务处理、性能调优等知识，对于构建高性能、高可用的数据库系统至关重要。

**关键要点：**
- **SQL 基础**：熟练掌握 DDL、DML、DQL
- **索引优化**：理解 B+Tree、索引类型、索引设计
- **事务与锁**：理解 ACID、隔离级别、锁机制
- **性能优化**：查询优化、索引优化、配置优化
- **高可用**：主从复制、分库分表
- **问题排查**：慢查询分析、性能监控

持续学习 MySQL 的新特性和最佳实践，结合实际业务场景优化数据库设计，是成为优秀数据库开发者的关键。

