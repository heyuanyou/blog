---
title: "跳表（Skip List）详解：基于 Golang 的实现与分析"
date: 2026-01-04
main: "算法"
sub: ["skiplist", "data-structure", "golang", "performance"]
summary: "深入讲解跳表数据结构，包括基础概念、数据结构设计、核心操作实现、时间复杂度分析、与平衡树对比、实际应用场景和 Golang 完整实现"
---

# 跳表（Skip List）详解：基于 Golang 的实现与分析

## 什么是跳表？

跳表（Skip List）是一种概率性的数据结构，由 William Pugh 在 1990 年提出。它是对有序链表的改进，通过添加多级索引来实现快速查找，时间复杂度可以达到 O(log n)。

**核心思想：**
> 在有序链表的基础上，添加多层索引，每一层都是下一层的"快速通道"，通过"跳跃"的方式快速定位目标元素。

**为什么需要跳表？**
- **有序链表**：查找需要 O(n)，插入和删除需要 O(n)
- **平衡树**：实现复杂，需要旋转操作
- **跳表**：实现简单，性能接近平衡树，平均 O(log n)

**跳表的特点：**
- **简单**：实现比平衡树简单
- **高效**：平均时间复杂度 O(log n)
- **概率性**：层级是随机生成的
- **有序**：保持元素有序

---

## 目录

- [基础概念](#基础概念)
- [数据结构设计](#数据结构设计)
- [核心操作实现](#核心操作实现)
- [概率性层级生成](#概率性层级生成)
- [时间复杂度分析](#时间复杂度分析)
- [空间复杂度分析](#空间复杂度分析)
- [与平衡树对比](#与平衡树对比)
- [完整实现](#完整实现)
- [优化技巧](#优化技巧)
- [实际应用场景](#实际应用场景)
- [常见问题](#常见问题)
- [总结](#总结)

---

## 基础概念

### 跳表的结构

跳表由多层有序链表组成：
- **第 0 层**：包含所有元素的有序链表
- **第 1 层**：包含部分元素的索引层
- **第 2 层**：包含更少元素的索引层
- **...**
- **第 k 层**：通常只有头节点和尾节点

**示例：**
```
Level 3:  -∞ ──────────────────────────────────────> +∞
Level 2:  -∞ ────────────> 20 ──────────────────────> +∞
Level 1:  -∞ ───> 10 ───> 20 ───> 30 ────────────────> +∞
Level 0:  -∞ ───> 10 ───> 20 ───> 30 ───> 40 ───> 50 ─> +∞
```

### 跳表的查找过程

查找元素 30 的过程：
1. 从最高层开始，向右移动直到下一个节点大于等于 30
2. 如果当前节点等于 30，返回找到
3. 如果下一个节点大于 30，向下移动一层
4. 重复步骤 1-3，直到找到或到达第 0 层

**查找路径：**
```
Level 3: -∞ ──────────────────────────────────────> +∞
         ↑
Level 2: -∞ ────────────> 20 ──────────────────────> +∞
         ↑              ↑
Level 1: -∞ ───> 10 ───> 20 ───> 30 ────────────────> +∞
         ↑              ↑        ↑
Level 0: -∞ ───> 10 ───> 20 ───> 30 ───> 40 ───> 50 ─> +∞
         ↑              ↑        ↑
        找到 30！
```

### 跳表的优势

**1. 实现简单**
- 不需要旋转操作
- 不需要维护平衡
- 代码量少

**2. 性能优秀**
- 平均时间复杂度 O(log n)
- 最坏情况 O(n)，但概率极低
- 实际性能接近平衡树

**3. 支持范围查询**
- 可以高效地查找范围内的所有元素
- 支持顺序遍历

**4. 并发友好**
- 可以设计成无锁或细粒度锁
- Redis 使用跳表实现有序集合

---

## 数据结构设计

### 节点结构

```go
// Node 表示跳表中的一个节点
type Node struct {
    key   int         // 节点的键值
    value interface{} // 节点的值（可以是任意类型）
    next  []*Node     // 每一层的下一个节点指针数组
}

// NewNode 创建一个新节点
func NewNode(key int, value interface{}, level int) *Node {
    return &Node{
        key:   key,
        value: value,
        next:  make([]*Node, level),
    }
}
```

### 跳表结构

```go
// SkipList 跳表结构
type SkipList struct {
    head      *Node   // 头节点（哨兵节点）
    level     int     // 当前最大层级
    maxLevel  int     // 最大允许层级
    length    int     // 元素个数
    prob      float64 // 概率因子（通常为 0.5）
}

// NewSkipList 创建一个新的跳表
func NewSkipList(maxLevel int, prob float64) *SkipList {
    head := NewNode(math.MinInt32, nil, maxLevel) // 头节点使用最小整数
    return &SkipList{
        head:     head,
        level:    1,
        maxLevel: maxLevel,
        length:   0,
        prob:     prob,
    }
}
```

### 设计要点

**1. 头节点（哨兵节点）**
- 使用 `-∞` 作为键值，确保所有元素都在它之后
- 头节点有 `maxLevel` 层，指向每一层的第一个节点

**2. 层级管理**
- `level`：当前实际使用的最大层级
- `maxLevel`：允许的最大层级（防止层级过高）

**3. 概率因子**
- `prob`：通常为 0.5，表示每个节点有 50% 的概率出现在上一层
- 可以通过调整概率因子来平衡性能和空间

---

## 核心操作实现

### 1. 查找操作

**算法思路：**
1. 从最高层开始查找
2. 在当前层向右移动，直到下一个节点大于等于目标键
3. 如果找到，返回节点；否则向下移动一层
4. 重复步骤 2-3，直到第 0 层

```go
// Search 查找指定键的节点
func (sl *SkipList) Search(key int) (*Node, bool) {
    current := sl.head
    
    // 从最高层向下查找
    for i := sl.level - 1; i >= 0; i-- {
        // 在当前层向右移动，直到下一个节点大于等于目标键
        for current.next[i] != nil && current.next[i].key < key {
            current = current.next[i]
        }
        
        // 如果找到目标键，返回节点
        if current.next[i] != nil && current.next[i].key == key {
            return current.next[i], true
        }
    }
    
    return nil, false
}
```

**时间复杂度：** O(log n) 平均，O(n) 最坏

### 2. 插入操作

**算法思路：**
1. 查找插入位置，记录每一层需要更新的节点
2. 随机生成新节点的层级
3. 创建新节点
4. 从下往上，更新每一层的指针

```go
// Insert 插入一个键值对
func (sl *SkipList) Insert(key int, value interface{}) bool {
    // 查找插入位置，记录每一层需要更新的节点
    update := make([]*Node, sl.maxLevel)
    current := sl.head
    
    // 从最高层向下查找
    for i := sl.level - 1; i >= 0; i-- {
        // 在当前层向右移动，直到下一个节点大于等于目标键
        for current.next[i] != nil && current.next[i].key < key {
            current = current.next[i]
        }
        update[i] = current
    }
    
    // 如果键已存在，更新值
    if current.next[0] != nil && current.next[0].key == key {
        current.next[0].value = value
        return true
    }
    
    // 随机生成新节点的层级
    newLevel := sl.randomLevel()
    
    // 如果新层级大于当前层级，更新层级
    if newLevel > sl.level {
        for i := sl.level; i < newLevel; i++ {
            update[i] = sl.head
        }
        sl.level = newLevel
    }
    
    // 创建新节点
    newNode := NewNode(key, value, newLevel)
    
    // 从下往上，更新每一层的指针
    for i := 0; i < newLevel; i++ {
        newNode.next[i] = update[i].next[i]
        update[i].next[i] = newNode
    }
    
    sl.length++
    return true
}
```

**时间复杂度：** O(log n) 平均

### 3. 删除操作

**算法思路：**
1. 查找要删除的节点，记录每一层需要更新的节点
2. 如果找到，从下往上更新每一层的指针
3. 更新跳表的层级（如果删除的是最高层的节点）

```go
// Delete 删除指定键的节点
func (sl *SkipList) Delete(key int) bool {
    // 查找要删除的节点，记录每一层需要更新的节点
    update := make([]*Node, sl.maxLevel)
    current := sl.head
    
    // 从最高层向下查找
    for i := sl.level - 1; i >= 0; i-- {
        // 在当前层向右移动，直到下一个节点大于等于目标键
        for current.next[i] != nil && current.next[i].key < key {
            current = current.next[i]
        }
        update[i] = current
    }
    
    // 检查是否找到要删除的节点
    target := current.next[0]
    if target == nil || target.key != key {
        return false
    }
    
    // 从下往上，更新每一层的指针
    for i := 0; i < sl.level; i++ {
        if update[i].next[i] != target {
            break
        }
        update[i].next[i] = target.next[i]
    }
    
    // 更新跳表的层级
    for sl.level > 1 && sl.head.next[sl.level-1] == nil {
        sl.level--
    }
    
    sl.length--
    return true
}
```

**时间复杂度：** O(log n) 平均

### 4. 范围查询

```go
// Range 返回指定范围内的所有节点
func (sl *SkipList) Range(minKey, maxKey int) []*Node {
    var result []*Node
    current := sl.head
    
    // 从最高层向下查找，找到第一个大于等于 minKey 的节点
    for i := sl.level - 1; i >= 0; i-- {
        for current.next[i] != nil && current.next[i].key < minKey {
            current = current.next[i]
        }
    }
    
    // 从第 0 层开始，遍历范围内的所有节点
    current = current.next[0]
    for current != nil && current.key <= maxKey {
        result = append(result, current)
        current = current.next[0]
    }
    
    return result
}
```

**时间复杂度：** O(log n + k)，其中 k 是范围内的元素个数

---

## 概率性层级生成

### 随机层级生成算法

跳表的核心是随机生成节点的层级。每个节点有 `prob` 的概率出现在上一层。

```go
// randomLevel 随机生成节点的层级
func (sl *SkipList) randomLevel() int {
    level := 1
    // 有 prob 的概率继续增加层级
    for rand.Float64() < sl.prob && level < sl.maxLevel {
        level++
    }
    return level
}
```

### 层级分布

假设 `prob = 0.5`：
- **第 0 层**：100% 的节点（所有节点）
- **第 1 层**：50% 的节点
- **第 2 层**：25% 的节点
- **第 3 层**：12.5% 的节点
- **...**

**期望层级数：**
- 期望层级数 = 1 / prob = 2（当 prob = 0.5 时）
- 平均每个节点出现在 2 层

### 概率因子对性能的影响

**prob = 0.5（推荐）：**
- 平衡性能和空间
- 平均查找路径长度约为 log₂(n)

**prob = 0.25：**
- 层级更高，查找更快
- 但空间开销更大

**prob = 0.75：**
- 层级更低，空间更省
- 但查找可能更慢

---

## 时间复杂度分析

### 查找操作

**平均情况：** O(log n)

**分析：**
- 每一层期望跳过 1/prob 个节点
- 当 prob = 0.5 时，每一层期望跳过 2 个节点
- 层级数期望为 log₂(n)
- 总时间复杂度：O(log n)

**最坏情况：** O(n)
- 当所有节点都在同一层时（概率极低）
- 退化为有序链表

### 插入操作

**平均情况：** O(log n)

**分析：**
1. 查找插入位置：O(log n)
2. 随机生成层级：O(1)
3. 更新指针：O(log n)
4. 总时间复杂度：O(log n)

### 删除操作

**平均情况：** O(log n)

**分析：**
1. 查找要删除的节点：O(log n)
2. 更新指针：O(log n)
3. 总时间复杂度：O(log n)

### 范围查询

**时间复杂度：** O(log n + k)

**分析：**
1. 查找范围的起始位置：O(log n)
2. 遍历范围内的 k 个元素：O(k)
3. 总时间复杂度：O(log n + k)

---

## 空间复杂度分析

### 空间复杂度

**平均情况：** O(n)

**分析：**
- 每个节点期望出现在 1/prob 层
- 当 prob = 0.5 时，每个节点期望出现在 2 层
- 总空间复杂度：O(n)

**最坏情况：** O(n × log n)
- 当所有节点都在最高层时（概率极低）

### 空间优化

**1. 限制最大层级**
```go
maxLevel := int(math.Log2(float64(expectedElements))) + 1
```

**2. 调整概率因子**
- 降低 prob 可以减少空间开销
- 但可能影响查找性能

**3. 使用压缩存储**
- 对于值较大的情况，可以只存储指针或引用

---

## 与平衡树对比

### 性能对比

| 操作 | 跳表（平均） | 跳表（最坏） | 平衡树（平均） | 平衡树（最坏） |
|------|-------------|-------------|--------------|--------------|
| **查找** | O(log n) | O(n) | O(log n) | O(log n) |
| **插入** | O(log n) | O(n) | O(log n) | O(log n) |
| **删除** | O(log n) | O(n) | O(log n) | O(log n) |
| **范围查询** | O(log n + k) | O(n) | O(log n + k) | O(log n + k) |

### 实现复杂度对比

| 方面 | 跳表 | 平衡树（AVL/红黑树） |
|------|------|-------------------|
| **实现难度** | 简单 | 复杂 |
| **代码量** | 少 | 多 |
| **旋转操作** | 不需要 | 需要 |
| **平衡维护** | 不需要 | 需要 |
| **调试难度** | 低 | 高 |

### 适用场景

**跳表适合：**
- 需要简单实现
- 对最坏情况要求不严格
- 需要范围查询
- 并发场景（可以设计成无锁）

**平衡树适合：**
- 需要保证最坏情况性能
- 对实现复杂度不敏感
- 不需要范围查询

---

## 完整实现

### 完整代码

```go
package main

import (
    "fmt"
    "math"
    "math/rand"
    "time"
)

// Node 表示跳表中的一个节点
type Node struct {
    key   int
    value interface{}
    next  []*Node
}

// NewNode 创建一个新节点
func NewNode(key int, value interface{}, level int) *Node {
    return &Node{
        key:   key,
        value: value,
        next:  make([]*Node, level),
    }
}

// SkipList 跳表结构
type SkipList struct {
    head     *Node
    level    int
    maxLevel int
    length   int
    prob     float64
}

// NewSkipList 创建一个新的跳表
func NewSkipList(maxLevel int, prob float64) *SkipList {
    if maxLevel <= 0 {
        maxLevel = 16 // 默认最大层级
    }
    if prob <= 0 || prob >= 1 {
        prob = 0.5 // 默认概率
    }
    
    head := NewNode(math.MinInt32, nil, maxLevel)
    return &SkipList{
        head:     head,
        level:    1,
        maxLevel: maxLevel,
        length:   0,
        prob:     prob,
    }
}

// randomLevel 随机生成节点的层级
func (sl *SkipList) randomLevel() int {
    level := 1
    for rand.Float64() < sl.prob && level < sl.maxLevel {
        level++
    }
    return level
}

// Search 查找指定键的节点
func (sl *SkipList) Search(key int) (*Node, bool) {
    current := sl.head
    
    for i := sl.level - 1; i >= 0; i-- {
        for current.next[i] != nil && current.next[i].key < key {
            current = current.next[i]
        }
        
        if current.next[i] != nil && current.next[i].key == key {
            return current.next[i], true
        }
    }
    
    return nil, false
}

// Insert 插入一个键值对
func (sl *SkipList) Insert(key int, value interface{}) bool {
    update := make([]*Node, sl.maxLevel)
    current := sl.head
    
    for i := sl.level - 1; i >= 0; i-- {
        for current.next[i] != nil && current.next[i].key < key {
            current = current.next[i]
        }
        update[i] = current
    }
    
    if current.next[0] != nil && current.next[0].key == key {
        current.next[0].value = value
        return true
    }
    
    newLevel := sl.randomLevel()
    
    if newLevel > sl.level {
        for i := sl.level; i < newLevel; i++ {
            update[i] = sl.head
        }
        sl.level = newLevel
    }
    
    newNode := NewNode(key, value, newLevel)
    
    for i := 0; i < newLevel; i++ {
        newNode.next[i] = update[i].next[i]
        update[i].next[i] = newNode
    }
    
    sl.length++
    return true
}

// Delete 删除指定键的节点
func (sl *SkipList) Delete(key int) bool {
    update := make([]*Node, sl.maxLevel)
    current := sl.head
    
    for i := sl.level - 1; i >= 0; i-- {
        for current.next[i] != nil && current.next[i].key < key {
            current = current.next[i]
        }
        update[i] = current
    }
    
    target := current.next[0]
    if target == nil || target.key != key {
        return false
    }
    
    for i := 0; i < sl.level; i++ {
        if update[i].next[i] != target {
            break
        }
        update[i].next[i] = target.next[i]
    }
    
    for sl.level > 1 && sl.head.next[sl.level-1] == nil {
        sl.level--
    }
    
    sl.length--
    return true
}

// Range 返回指定范围内的所有节点
func (sl *SkipList) Range(minKey, maxKey int) []*Node {
    var result []*Node
    current := sl.head
    
    for i := sl.level - 1; i >= 0; i-- {
        for current.next[i] != nil && current.next[i].key < minKey {
            current = current.next[i]
        }
    }
    
    current = current.next[0]
    for current != nil && current.key <= maxKey {
        result = append(result, current)
        current = current.next[0]
    }
    
    return result
}

// Size 返回跳表中元素的个数
func (sl *SkipList) Size() int {
    return sl.length
}

// Print 打印跳表的结构（用于调试）
func (sl *SkipList) Print() {
    fmt.Printf("SkipList (level=%d, length=%d):\n", sl.level, sl.length)
    for i := sl.level - 1; i >= 0; i-- {
        fmt.Printf("Level %d: ", i)
        current := sl.head.next[i]
        for current != nil {
            fmt.Printf("%d -> ", current.key)
            current = current.next[i]
        }
        fmt.Println("nil")
    }
}

// 使用示例
func main() {
    rand.Seed(time.Now().UnixNano())
    
    // 创建一个跳表
    sl := NewSkipList(16, 0.5)
    
    // 插入元素
    keys := []int{10, 20, 30, 40, 50, 25, 35, 15}
    for _, key := range keys {
        sl.Insert(key, fmt.Sprintf("value-%d", key))
    }
    
    // 打印跳表结构
    sl.Print()
    
    // 查找元素
    if node, found := sl.Search(30); found {
        fmt.Printf("Found: key=%d, value=%v\n", node.key, node.value)
    }
    
    // 范围查询
    nodes := sl.Range(20, 40)
    fmt.Println("Range [20, 40]:")
    for _, node := range nodes {
        fmt.Printf("  key=%d, value=%v\n", node.key, node.value)
    }
    
    // 删除元素
    if sl.Delete(30) {
        fmt.Println("Deleted key 30")
    }
    
    sl.Print()
}
```

### 测试代码

```go
// 性能测试
func BenchmarkSkipListInsert(b *testing.B) {
    sl := NewSkipList(16, 0.5)
    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        sl.Insert(i, i)
    }
}

func BenchmarkSkipListSearch(b *testing.B) {
    sl := NewSkipList(16, 0.5)
    for i := 0; i < 10000; i++ {
        sl.Insert(i, i)
    }
    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        sl.Search(i % 10000)
    }
}

func BenchmarkSkipListDelete(b *testing.B) {
    sl := NewSkipList(16, 0.5)
    for i := 0; i < 10000; i++ {
        sl.Insert(i, i)
    }
    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        sl.Delete(i % 10000)
    }
}
```

---

## 优化技巧

### 1. 动态调整最大层级

```go
// 根据预期元素个数动态计算最大层级
func calculateMaxLevel(expectedElements int) int {
    if expectedElements <= 0 {
        return 16
    }
    return int(math.Log2(float64(expectedElements))) + 1
}
```

### 2. 使用对象池

```go
var nodePool = sync.Pool{
    New: func() interface{} {
        return &Node{}
    },
}

func (sl *SkipList) getNode(key int, value interface{}, level int) *Node {
    node := nodePool.Get().(*Node)
    node.key = key
    node.value = value
    if cap(node.next) < level {
        node.next = make([]*Node, level)
    } else {
        node.next = node.next[:level]
    }
    return node
}

func (sl *SkipList) putNode(node *Node) {
    node.key = 0
    node.value = nil
    node.next = node.next[:0]
    nodePool.Put(node)
}
```

### 3. 批量操作优化

```go
// BatchInsert 批量插入，减少层级更新
func (sl *SkipList) BatchInsert(items []Item) {
    // 先排序
    sort.Slice(items, func(i, j int) bool {
        return items[i].Key < items[j].Key
    })
    
    // 批量插入
    for _, item := range items {
        sl.Insert(item.Key, item.Value)
    }
}
```

### 4. 内存对齐优化

```go
// 使用内存对齐减少内存占用
type Node struct {
    key   int
    value interface{}
    // 使用 uint8 存储层级信息
    level uint8
    next  []*Node
}
```

---

## 实际应用场景

### 1. Redis 有序集合（Sorted Set）

Redis 使用跳表实现有序集合：
- **查找**：O(log n) 查找成员
- **插入**：O(log n) 插入成员
- **范围查询**：O(log n + k) 获取范围内的成员
- **排名**：O(log n) 获取成员的排名

### 2. LevelDB / RocksDB

LevelDB 和 RocksDB 使用跳表作为内存中的数据结构：
- **MemTable**：使用跳表存储键值对
- **写入性能**：跳表比平衡树更适合写入密集的场景

### 3. 时间序列数据库

时间序列数据库使用跳表存储时间序列数据：
- **时间范围查询**：高效查询时间范围内的数据
- **插入性能**：时间序列数据通常是顺序插入的

### 4. 分布式系统中的路由表

分布式系统使用跳表实现路由表：
- **节点查找**：快速查找负责某个键的节点
- **一致性哈希**：结合一致性哈希使用

### 5. 游戏排行榜

游戏排行榜使用跳表实现：
- **排名查询**：O(log n) 查询玩家排名
- **范围查询**：O(log n + k) 查询前 k 名玩家
- **更新排名**：O(log n) 更新玩家分数

---

## 常见问题

### 1. 跳表的最坏情况性能如何？

**问题：**
跳表的最坏情况时间复杂度是 O(n)，是否会影响实际使用？

**回答：**
- 最坏情况（所有节点在同一层）的概率极低
- 对于 n 个节点，概率约为 (1/prob)^n
- 当 n = 1000, prob = 0.5 时，概率约为 10^-300
- 实际使用中几乎不会遇到最坏情况

### 2. 如何选择概率因子？

**问题：**
如何选择最优的概率因子？

**回答：**
- **prob = 0.5**：平衡性能和空间，推荐使用
- **prob = 0.25**：层级更高，查找更快，但空间更大
- **prob = 0.75**：层级更低，空间更省，但查找可能更慢
- 大多数情况下，0.5 是最优选择

### 3. 跳表是否线程安全？

**问题：**
跳表是否支持并发访问？

**回答：**
- 基础实现不是线程安全的
- 可以通过以下方式实现线程安全：
  - **互斥锁**：简单但性能较差
  - **读写锁**：适合读多写少的场景
  - **无锁实现**：使用 CAS 操作，性能最好但实现复杂

### 4. 跳表与平衡树的性能对比？

**问题：**
跳表和平衡树哪个性能更好？

**回答：**
- **平均性能**：跳表和平衡树都是 O(log n)，性能相近
- **最坏性能**：平衡树保证 O(log n)，跳表最坏是 O(n)
- **实现复杂度**：跳表更简单
- **实际性能**：跳表通常更快，因为实现简单，缓存友好

### 5. 如何处理重复键？

**问题：**
跳表如何处理重复的键？

**回答：**
- **方案 1**：更新值（当前实现）
- **方案 2**：允许重复键，使用链表存储多个值
- **方案 3**：使用复合键（key + timestamp）

```go
// 方案 2：允许重复键
type Node struct {
    key    int
    values []interface{} // 存储多个值
    next   []*Node
}
```

### 6. 如何实现并发安全的跳表？

**问题：**
如何实现支持并发访问的跳表？

**回答：**
```go
// 使用读写锁
type ConcurrentSkipList struct {
    sl    *SkipList
    mutex sync.RWMutex
}

func (csl *ConcurrentSkipList) Search(key int) (*Node, bool) {
    csl.mutex.RLock()
    defer csl.mutex.RUnlock()
    return csl.sl.Search(key)
}

func (csl *ConcurrentSkipList) Insert(key int, value interface{}) bool {
    csl.mutex.Lock()
    defer csl.mutex.Unlock()
    return csl.sl.Insert(key, value)
}
```

---

## 总结

跳表是一种优秀的数据结构，具有以下特点：

**优势：**
- **实现简单**：比平衡树更容易实现
- **性能优秀**：平均时间复杂度 O(log n)
- **支持范围查询**：高效的范围查询操作
- **并发友好**：可以设计成无锁或细粒度锁

**适用场景：**
- Redis 有序集合
- 时间序列数据库
- 游戏排行榜
- 分布式路由表

**关键要点：**
- 使用概率性层级生成，平衡性能和空间
- 推荐使用 prob = 0.5 作为概率因子
- 根据预期元素个数动态调整最大层级
- 注意线程安全，根据场景选择合适的并发控制方式

掌握跳表对于理解现代数据库和分布式系统的实现原理非常重要。

---

## 参考资料

- [Skip Lists: A Probabilistic Alternative to Balanced Trees](https://15721.courses.cs.cmu.edu/spring2018/papers/08-oltpindexes1/pugh-skiplists-cacm1990.pdf)
- [Redis 源码：跳表实现](https://github.com/redis/redis/blob/unstable/src/t_zset.c)
- [LevelDB 源码：跳表实现](https://github.com/google/leveldb/blob/master/db/skiplist.h)

