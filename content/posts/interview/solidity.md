---
title: "Solidity 面试题"
date: 2025-12-26T14:24:00+08:00
draft: false
tags: ["solidity", "blockchain", "ethereum", "interview"]
author: "Henry"
showToc: true
TocOpen: false
hidemeta: false
comments: false
description: "Solidity 智能合约开发面试题整理，涵盖基础到高级的各个方面"
ShowReadingTime: true
ShowBreadCrumbs: true
ShowPostNavLinks: true
ShowWordCount: true
UseHugoToc: true
---

# Solidity 面试题

## 目录

- [基础概念](#基础概念)
- [数据类型与变量](#数据类型与变量)
- [函数与修饰符](#函数与修饰符)
- [继承与接口](#继承与接口)
- [事件与日志](#事件与日志)
- [Gas 优化](#gas-优化)
- [安全性问题](#安全性问题)
- [智能合约开发最佳实践](#智能合约开发最佳实践)
- [高级特性](#高级特性)
- [常见漏洞与防护](#常见漏洞与防护)

---

## 基础概念

### 1. 什么是 Solidity？它有哪些特点？

**答案：**
Solidity 是一种面向合约的高级编程语言，用于在以太坊虚拟机（EVM）上编写智能合约。主要特点包括：

- **静态类型语言**：编译时进行类型检查
- **面向对象**：支持继承、库和复杂的用户定义类型
- **图灵完备**：可以执行任意计算
- **事件系统**：用于日志记录和与前端交互
- **内置安全特性**：如溢出检查（Solidity 0.8.0+）

### 2. 智能合约的生命周期是什么？

**答案：**
智能合约的生命周期包括：

1. **编写**：使用 Solidity 编写合约代码
2. **编译**：使用 Solidity 编译器将代码编译成字节码
3. **部署**：将字节码部署到区块链上，获得合约地址
4. **执行**：通过调用合约函数来执行合约逻辑
5. **销毁**：使用 `selfdestruct()` 函数销毁合约（不可逆）

### 3. 什么是 EVM（以太坊虚拟机）？

**答案：**
EVM 是以太坊网络中的运行时环境，用于执行智能合约。特点：

- **隔离性**：每个合约在独立的环境中运行
- **确定性**：相同输入总是产生相同输出
- **Gas 机制**：每个操作消耗 Gas，防止无限循环
- **栈式架构**：使用栈来存储临时数据

### 4. 什么是 Gas？Gas Price 和 Gas Limit 的区别？

**答案：**
- **Gas**：执行操作的计算单位，用于衡量计算成本
- **Gas Price**：愿意为每个 Gas 单位支付的价格（Gwei）
- **Gas Limit**：愿意为交易支付的最大 Gas 数量

**总费用 = Gas Used × Gas Price**

Gas Limit 是保护机制，防止代码错误导致无限消耗。

### 5. 调用合约的 selfdestruct() 会发生什么？

**答案：**
`selfdestruct()` 是 Solidity 中用于销毁合约的函数，调用后会发生以下情况：

**1. 余额转移**
```solidity
contract Destructible {
    function destroy() public {
        // 将合约余额转移到指定地址
        selfdestruct(payable(msg.sender));
    }
}
```
- 合约的所有 ETH 余额会立即转移到指定的接收地址
- 即使接收地址是合约且没有 payable fallback，转账也会成功
- 这是唯一可以强制向合约发送 ETH 的方式

**2. 代码删除**
- 合约的字节码从区块链上删除
- 合约地址仍然存在，但调用会失败（没有代码）
- 合约地址永久保留，无法重新部署到同一地址

**3. 存储清理**
- 合约的所有存储数据被清除
- 状态变量重置为默认值
- 这是 Gas 退款机制的一部分（EIP-3529 后已移除）

**4. 不可逆性**
- 操作完全不可逆
- 一旦执行，无法撤销
- 合约地址永久失效

**重要特性：**

**强制转账能力：**
```solidity
contract ForcedTransfer {
    // 即使目标合约没有 payable 函数，也能收到 ETH
    function forceSend(address target) public {
        selfdestruct(payable(target));
    }
}
```

**Gas 成本：**
- `selfdestruct` 操作本身消耗约 5000 Gas
- 之前版本有 Gas 退款（清除存储），但 EIP-3529 后已移除

**安全考虑：**
```solidity
contract SecureContract {
    address public owner;
    bool public destroyed;
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }
    
    modifier notDestroyed() {
        require(!destroyed, "Contract destroyed");
        _;
    }
    
    function destroy() public onlyOwner notDestroyed {
        destroyed = true;
        selfdestruct(payable(owner));
    }
}
```

**注意事项：**
1. **权限控制**：必须确保只有授权地址可以调用
2. **接收地址验证**：验证接收地址不是零地址
3. **状态检查**：确保合约未被销毁
4. **余额检查**：即使余额为 0 也可以调用

**与普通转账的区别：**

| 特性 | selfdestruct | transfer/send/call |
|------|-------------|-------------------|
| 目标限制 | 可以是任何地址 | 需要 payable 或 fallback |
| 合约状态 | 销毁合约 | 合约继续存在 |
| 可逆性 | 不可逆 | 可逆（可退回） |
| Gas 成本 | ~5000 Gas | 21000+ Gas |
| 用途 | 合约清理 | 正常转账 |

**实际应用场景：**
- **临时合约**：完成特定任务后销毁
- **资金回收**：将合约余额返还给所有者
- **升级模式**：旧合约销毁，资金转移到新合约
- **测试合约**：测试完成后清理

**EIP-4758 提案：**
未来可能移除 `selfdestruct` 操作码，改用更安全的替代方案。

---

## 数据类型与变量

### 6. Solidity 有哪些基本数据类型？

**答案：**
- **布尔型**：`bool`（true/false）
- **整数型**：
  - 有符号：`int8` 到 `int256`（步长 8）
  - 无符号：`uint8` 到 `uint256`（步长 8）
  - 默认：`int256` 和 `uint256`
- **地址型**：`address`（20 字节）和 `address payable`
- **字节型**：`bytes1` 到 `bytes32`，`bytes`（动态），`string`（UTF-8）
- **定长数组**：`uint[5]`
- **动态数组**：`uint[]`
- **映射**：`mapping(address => uint256)`
- **结构体**：`struct`

### 7. storage、memory 和 calldata 的区别？

**答案：**

| 位置 | 存储位置 | 生命周期 | 成本 | 可变性 |
|------|---------|---------|------|--------|
| **storage** | 区块链状态 | 永久 | 高 | 可变 |
| **memory** | 临时内存 | 函数执行期间 | 中 | 可变 |
| **calldata** | 调用数据 | 函数执行期间 | 低 | 不可变（只读） |

```solidity
contract Example {
    uint[] storageArray; // storage
    
    function example(uint[] memory memArray, uint[] calldata calldataArray) public {
        // memArray 可以修改
        memArray[0] = 1;
        
        // calldataArray 不能修改（只读）
        // calldataArray[0] = 1; // 编译错误
    }
}
```

### 8. 什么是状态变量、局部变量和全局变量？

**答案：**
- **状态变量**：存储在区块链上的变量，永久保存
- **局部变量**：函数内部定义的变量，函数执行完后销毁
- **全局变量**：Solidity 提供的特殊变量，如 `msg.sender`、`block.timestamp`、`tx.origin` 等

### 9. mapping 和数组的区别？什么时候用哪个？

**答案：**

| 特性 | mapping | 数组 |
|------|---------|------|
| 键类型 | 任意类型 | 只能是 uint |
| 查找效率 | O(1) | O(n) |
| 遍历 | 不支持 | 支持 |
| 删除 | 设为默认值 | 可删除元素 |
| Gas 成本 | 固定 | 随长度增长 |

**使用场景：**
- **mapping**：需要快速查找、键值对关系
- **数组**：需要遍历、保持顺序、需要长度信息

### 10. 什么是 bytes32 和 string？如何选择？

**答案：**
- **bytes32**：固定长度 32 字节，Gas 成本低，适合固定长度数据
- **string**：动态长度 UTF-8 编码，Gas 成本高，适合可变长度文本

**选择建议：**
- 固定长度（如哈希值）→ `bytes32`
- 可变长度文本 → `string`
- 需要字符串操作 → `string`

---

## 函数与修饰符

### 11. 函数的可见性有哪些？有什么区别？

**答案：**
- **public**：内部和外部都可调用，自动生成 getter 函数
- **external**：只能外部调用，不能内部调用
- **internal**：只能内部和继承合约调用
- **private**：只能当前合约调用

```solidity
contract Visibility {
    function publicFunc() public {}      // 内外都可调用
    function externalFunc() external {}  // 只能外部调用
    function internalFunc() internal {}  // 内部和继承合约
    function privateFunc() private {}    // 仅当前合约
}
```

### 12. 什么是函数修饰符（modifier）？如何使用？

**答案：**
修饰符用于在执行函数前/后添加检查逻辑，实现代码复用。

**执行顺序：**
- `_;` 的位置决定了原函数的执行时机
- `_;` **之前**的代码：在原函数执行**前**运行（前置检查）
- `_;` **之后**的代码：在原函数执行**后**运行（后置处理）

```solidity
contract ModifierExample {
    address public owner;
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _; // 执行原函数
    }
    
    modifier validAddress(address addr) {
        require(addr != address(0), "Invalid address");
        _; // 先检查，再执行原函数
    }
    
    // 执行顺序：onlyOwner 检查 → validAddress 检查 → changeOwner 函数体
    function changeOwner(address newOwner) public onlyOwner validAddress(newOwner) {
        owner = newOwner;
    }
    
    // 错误示例：检查放在 _; 之后
    modifier badModifier(address addr) {
        _; // 先执行函数
        require(addr != address(0), "Too late!"); // 函数已执行，检查无意义
    }
}
```

**注意事项：**
- 验证类检查应该在 `_;` **之前**（前置检查）
- 清理类操作可以在 `_;` **之后**（后置处理）
- 多个 modifier 按声明顺序执行

### 13. view、pure 和 payable 函数的区别？

**答案：**
- **view**：只读取状态，不修改，不消耗 Gas（外部调用时）
- **pure**：不读取也不修改状态，不消耗 Gas（外部调用时）
- **payable**：可以接收以太币

```solidity
contract Example {
    uint public value;
    
    function getValue() public view returns (uint) {
        return value; // 只读
    }
    
    function calculate(uint a, uint b) public pure returns (uint) {
        return a + b; // 不访问状态
    }
    
    function deposit() public payable {
        // 可以接收 ETH
    }
}
```

### 14. 函数重载（overloading）是什么？

**答案：**
函数重载允许在同一合约中定义多个同名函数，但参数类型或数量必须不同。

```solidity
contract Overload {
    function transfer(address to, uint amount) public {}
    function transfer(address to, uint amount, bytes memory data) public {}
    // 参数不同，可以重载
}
```

### 15. receive() 和 fallback() 函数的区别？

**答案：**

`receive()` 和 `fallback()` 都是特殊的接收函数，用于处理向合约发送 ETH 或调用不存在函数的情况。

**核心区别：**

| 函数 | 触发条件 | 函数签名 | 用途 |
|------|---------|---------|------|
| **receive()** | 接收 ETH 且**没有任何数据** | `receive() external payable` | 专门处理纯 ETH 转账 |
| **fallback()** | 1. 调用**不存在的函数**<br>2. 接收 ETH 但**没有 receive()** | `fallback() external payable`<br>或 `fallback() external` | 兜底处理函数 |

**详细说明：**

**1. receive() 函数**
- **唯一用途**：接收纯 ETH 转账（没有调用数据）
- **必须声明为**：`external payable`
- **触发场景**：直接向合约地址发送 ETH，不调用任何函数

```solidity
contract ReceiveExample {
    event Received(address sender, uint amount);
    
    // 专门处理纯 ETH 转账
    receive() external payable {
        emit Received(msg.sender, msg.value);
        // msg.value 包含接收的 ETH 数量
    }
    
    // 如果只有 receive()，调用不存在的函数会失败
    // 因为没有 fallback() 处理
}
```

**2. fallback() 函数**
- **用途1**：处理调用不存在的函数
- **用途2**：如果没有 receive()，也可以接收 ETH
- **可以声明为**：`external payable`（可接收 ETH）或 `external`（不接收 ETH）

```solidity
contract FallbackExample {
    event FallbackCalled(bytes data);
    
    // 处理调用不存在的函数
    fallback() external payable {
        emit FallbackCalled(msg.data);
        // msg.data 包含调用数据
    }
    
    // 如果没有 receive()，这个也可以接收 ETH
    // 但 fallback() 会收到调用数据（即使为空）
}
```

**3. 完整示例：理解执行流程**

```solidity
contract CompleteExample {
    event Received(address sender, uint amount);
    event FallbackCalled(bytes data, uint value);
    
    // 情况1：纯 ETH 转账（无数据）
    receive() external payable {
        emit Received(msg.sender, msg.value);
        // 只有这种情况会调用 receive()
    }
    
    // 情况2：调用不存在的函数，或接收 ETH 但没有 receive()
    fallback() external payable {
        emit FallbackCalled(msg.data, msg.value);
        // msg.data: 调用数据（函数选择器 + 参数）
        // msg.value: 发送的 ETH 数量
    }
    
    // 正常函数
    function deposit() public payable {
        // 这个函数存在，不会被 fallback() 处理
    }
}
```

**执行优先级（重要！）：**

```
向合约发送交易
    ↓
有调用数据（msg.data 不为空）？
    ├─ 是 → 查找函数选择器
    │       ├─ 找到 → 执行对应函数
    │       └─ 未找到 → 执行 fallback()
    │
    └─ 否（纯 ETH 转账）
            ├─ 有 receive()？ → 执行 receive()
            └─ 无 receive()？ → 执行 fallback()
```

**实际调用示例：**

```solidity
// 假设合约地址是 0x1234...

// 场景1：纯 ETH 转账（推荐方式）
// 前端：sendTransaction({ to: "0x1234...", value: "1000000000000000000" })
// 结果：调用 receive()（如果存在），否则调用 fallback()

// 场景2：调用不存在的函数
// 前端：contract.call("nonExistentFunction()")
// 结果：调用 fallback()

// 场景3：调用存在的函数
// 前端：contract.deposit({ value: "1000000000000000000" })
// 结果：调用 deposit()，不调用 receive() 或 fallback()

// 场景4：调用不存在的函数并发送 ETH
// 前端：contract.call("nonExistentFunction()", { value: "1000000000000000000" })
// 结果：调用 fallback()（即使有 receive()，因为有调用数据）
```

**常见组合模式：**

```solidity
// 模式1：只接收 ETH，不接受其他调用
contract ETHReceiver {
    receive() external payable {
        // 只处理纯 ETH 转账
    }
    // 没有 fallback()，调用不存在的函数会 revert
}

// 模式2：接收 ETH 并处理未知调用
contract FlexibleReceiver {
    receive() external payable {
        // 处理纯 ETH 转账
    }
    
    fallback() external payable {
        // 处理调用不存在的函数
        // 也可以接收 ETH（如果没有 receive()）
    }
}

// 模式3：只处理未知调用，不接收 ETH
contract NoETHReceiver {
    fallback() external {
        // 不接收 ETH，只处理未知函数调用
        // 注意：没有 payable 关键字
    }
}
```

**注意事项：**
1. **receive() 优先级更高**：纯 ETH 转账时，优先调用 receive()
2. **fallback() 是兜底**：如果没有 receive()，fallback() 可以接收 ETH
3. **调用数据决定行为**：有调用数据 → fallback()，无调用数据 → receive()
4. **Gas 成本**：receive() 通常比 fallback() 更省 Gas（因为不需要处理调用数据）
5. **安全考虑**：如果合约不应该接收 ETH，不要声明 `payable`

---

## 继承与接口

### 16. Solidity 支持多重继承吗？如何工作？

**答案：**
支持。Solidity 支持一个合约同时继承多个合约，使用 **C3 线性化算法**解决钻石继承问题。

**什么是多重继承？**

多重继承是指一个合约可以同时继承多个父合约，继承所有父合约的功能。

```solidity
// 单一继承
contract Child is Parent {
    // 只继承 Parent
}

// 多重继承
contract Child is Parent1, Parent2, Parent3 {
    // 继承 Parent1, Parent2, Parent3
}
```

**钻石继承问题（Diamond Problem）**

当多个父合约继承自同一个祖先时，会产生"钻石继承"结构：

```
        A
       / \
      B   C
       \ /
        D
```

问题：如果 A、B、C 都有同名函数 `foo()`，D 调用 `super.foo()` 时应该调用哪个？

**C3 线性化算法**

Solidity 使用 C3 线性化算法确定继承顺序，规则是：**最右优先（Right-to-Left）**

```solidity
contract A {
    function foo() public virtual returns (string memory) {
        return "A";
    }
}

contract B is A {
    function foo() public virtual override returns (string memory) {
        return "B";
    }
}

contract C is A {
    function foo() public virtual override returns (string memory) {
        return "C";
    }
}

contract D is B, C {
    function foo() public override(B, C) returns (string memory) {
        return super.foo(); // 调用 C.foo()（最右优先）
    }
}
```

**继承顺序解析：**

对于 `contract D is B, C`：
1. **继承顺序**：从左到右是 `B, C`
2. **C3 线性化结果**：`D -> C -> B -> A`
3. **super 调用顺序**：`super.foo()` 会调用**最右**的父合约，即 `C.foo()`

**详细示例：理解调用链**

```solidity
contract A {
    function test() public virtual returns (string memory) {
        return "A";
    }
}

contract B is A {
    function test() public virtual override returns (string memory) {
        return string.concat("B -> ", super.test());
        // super.test() 调用 A.test()
    }
}

contract C is A {
    function test() public virtual override returns (string memory) {
        return string.concat("C -> ", super.test());
        // super.test() 调用 A.test()
    }
}

contract D is B, C {
    function test() public override(B, C) returns (string memory) {
        return string.concat("D -> ", super.test());
        // super.test() 调用 C.test()（最右优先）
    }
}

// 调用 D.test() 的结果：
// "D -> C -> A"
// 因为：D -> C -> B -> A（C3 线性化）
// super 从 C 开始，C 调用 A
```

**继承顺序的重要性**

```solidity
// 顺序1：D is B, C
contract D1 is B, C {
    // C3 顺序：D1 -> C -> B -> A
    // super.foo() 调用 C.foo()
}

// 顺序2：D is C, B（顺序相反）
contract D2 is C, B {
    // C3 顺序：D2 -> B -> C -> A
    // super.foo() 调用 B.foo()
}
```

**实际应用示例：**

```solidity
// 基础合约
contract Ownable {
    address public owner;
    
    constructor() {
        owner = msg.sender;
    }
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }
}

contract Pausable {
    bool public paused;
    
    modifier whenNotPaused() {
        require(!paused, "Paused");
        _;
    }
    
    function pause() public {
        paused = true;
    }
}

contract ReentrancyGuard {
    bool private locked;
    
    modifier nonReentrant() {
        require(!locked, "Reentrant call");
        locked = true;
        _;
        locked = false;
    }
}

// 多重继承：组合多个功能
contract SecureContract is Ownable, Pausable, ReentrancyGuard {
    function withdraw() public onlyOwner whenNotPaused nonReentrant {
        // 同时拥有三个父合约的功能
        // 1. onlyOwner：只有 owner 可以调用
        // 2. whenNotPaused：未暂停时才能调用
        // 3. nonReentrant：防止重入攻击
    }
}
```

**override 关键字的使用**

当多个父合约有同名函数时，必须明确指定要覆盖哪些父合约：

```solidity
contract A {
    function foo() public virtual returns (string memory) {
        return "A";
    }
}

contract B is A {
    function foo() public virtual override returns (string memory) {
        return "B";
    }
}

contract C is A {
    function foo() public virtual override returns (string memory) {
        return "C";
    }
}

contract D is B, C {
    // 必须明确指定覆盖 B 和 C
    function foo() public override(B, C) returns (string memory) {
        return "D";
    }
}
```

**构造函数调用顺序**

构造函数按继承顺序**从右到左**调用：

```solidity
contract A {
    constructor() {
        // 最后调用
    }
}

contract B is A {
    constructor() {
        // 第二个调用
    }
}

contract C is A {
    constructor() {
        // 第一个调用
    }
}

contract D is B, C {
    constructor() B() C() {
        // 调用顺序：C -> B -> A -> D
    }
}
```

**注意事项：**

1. **继承顺序很重要**：`is B, C` 和 `is C, B` 会产生不同的 C3 线性化结果
2. **必须明确 override**：如果多个父合约有同名函数，必须明确指定覆盖哪些
3. **构造函数参数**：如果父合约构造函数需要参数，子合约必须提供
4. **状态变量冲突**：多个父合约不能有同名的状态变量
5. **Gas 成本**：继承链越长，部署和执行成本越高

**常见模式：**

```solidity
// 模式1：功能组合（推荐）
contract MyToken is ERC20, Ownable, Pausable {
    // 组合多个标准功能
}

// 模式2：接口实现
contract MyContract is IERC20, IERC721 {
    // 实现多个接口
}

// 模式3：功能扩展
contract BaseContract {
    // 基础功能
}

contract ExtendedContract is BaseContract, AdditionalFeatures {
    // 扩展功能
}
```

### 17. abstract 合约和 interface 的区别？

**答案：**

| 特性 | abstract 合约 | interface |
|------|--------------|-----------|
| 状态变量 | 可以有 | 不能有 |
| 构造函数 | 可以有 | 不能有 |
| 函数实现 | 可以有 | 不能有 |
| 继承 | 可以继承其他合约 | 只能继承其他接口 |
| 可见性 | 可以是 internal | 必须是 external |

```solidity
// Abstract 合约
abstract contract AbstractContract {
    uint public value; // 可以有状态变量
    
    function mustImplement() public virtual; // 必须实现
    function canHaveImplementation() public virtual {
        // 可以有实现
    }
}

// Interface
interface IERC20 {
    function transfer(address to, uint amount) external returns (bool);
    // 不能有状态变量和实现
}
```

### 18. 什么是函数选择器（function selector）？

**答案：**
函数选择器是函数签名的前 4 字节 Keccak256 哈希值，用于标识要调用的函数。

```solidity
contract SelectorExample {
    function transfer(address to, uint amount) public {
        // 选择器 = bytes4(keccak256("transfer(address,uint256)"))
    }
    
    function callBySelector() public {
        bytes4 selector = this.transfer.selector;
        // 或 bytes4(keccak256("transfer(address,uint256)"))
    }
}
```

---

## 事件与日志

### 19. 什么是事件（Event）？为什么使用事件？

**答案：**
事件是智能合约向外部世界发送通知的机制，数据存储在日志中。

**用途：**
- **前端监听**：DApp 前端可以监听事件更新 UI
- **日志记录**：记录重要操作和状态变化
- **Gas 优化**：比存储变量更便宜
- **链下索引**：便于链下系统索引和查询

```solidity
contract EventExample {
    event Transfer(address indexed from, address indexed to, uint amount);
    
    function transfer(address to, uint amount) public {
        emit Transfer(msg.sender, to, amount);
    }
}
```

### 20. indexed 参数的作用？

**答案：**
`indexed` 参数可以被过滤查询，最多 3 个 indexed 参数。

```solidity
event Transfer(address indexed from, address indexed to, uint amount);

// 前端可以这样过滤：
// 监听特定地址的转账
contract.on("Transfer", { from: "0x..." }, callback);
```

### 21. 事件和日志的区别？

**答案：**
- **事件**：Solidity 代码中的声明
- **日志**：事件触发后存储在区块链上的数据

事件是接口，日志是实际存储的数据结构。

---

## Gas 优化

### 22. 如何优化 Gas 消耗？

**答案：**

**1. 变量打包**
```solidity
// 差：占用 3 个存储槽
uint128 a;
uint256 b;
uint128 c;

// 好：a 和 c 打包在一个槽
uint128 a;
uint128 c;
uint256 b;
```

**2. 使用 uint256**
```solidity
// 差：需要额外操作
uint8 count;

// 好：EVM 原生支持
uint256 count;
```

**3. 缓存存储变量**
```solidity
// 差：多次读取存储
for (uint i = 0; i < array.length; i++) {
    total += array[i];
}

// 好：缓存长度
uint length = array.length;
for (uint i = 0; i < length; i++) {
    total += array[i];
}
```

**4. 使用 calldata 代替 memory**
```solidity
// 好：calldata 更便宜
function process(uint[] calldata data) public {}
```

**5. 短路评估**
```solidity
// 好：如果第一个条件为假，不评估第二个
if (condition1 && condition2) {}
```

### 23. 存储槽（storage slot）是什么？

**答案：**
存储槽是 EVM 中 32 字节的存储单元。每个状态变量占用一个或多个槽。

**打包规则：**
- 连续的小类型变量可以打包在一个槽中
- 每个槽 32 字节
- 结构体和数组从新槽开始

```solidity
contract SlotExample {
    uint128 a;  // slot 0 (前 16 字节)
    uint128 b;  // slot 0 (后 16 字节)
    uint256 c;  // slot 1 (完整槽)
}
```

### 24. 为什么循环很消耗 Gas？

**答案：**
- 每次迭代都执行操作码
- 存储读写操作成本高
- 无法提前知道循环次数

**优化方法：**
- 限制循环次数
- 使用映射代替数组查找
- 批量操作代替多次单独操作

---

## 安全性问题

### 25. 什么是重入攻击（Reentrancy Attack）？如何防护？

**答案：**
重入攻击是攻击者在外部调用完成前再次调用函数，可能导致状态不一致。

```solidity
// 漏洞代码
contract Vulnerable {
    mapping(address => uint) balances;
    
    function withdraw() public {
        uint amount = balances[msg.sender];
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
        balances[msg.sender] = 0; // 太晚了！
    }
}

// 防护方法 1：Checks-Effects-Interactions 模式
function withdraw() public {
    uint amount = balances[msg.sender];
    balances[msg.sender] = 0; // 先更新状态
    (bool success, ) = msg.sender.call{value: amount}("");
    require(success, "Transfer failed");
}

// 防护方法 2：使用 ReentrancyGuard
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

contract Safe is ReentrancyGuard {
    function withdraw() public nonReentrant {
        // 安全代码
    }
}
```

### 26. 整数溢出如何防护？

**答案：**
Solidity 0.8.0+ 自动检查溢出，之前版本需要使用 SafeMath。

```solidity
// Solidity 0.8.0+
uint256 a = type(uint256).max;
a += 1; // 自动 revert

// 0.7.x 及之前
import "@openzeppelin/contracts/utils/math/SafeMath.sol";
using SafeMath for uint256;
uint256 a = a.add(1); // 安全加法
```

### 27. 什么是时间戳依赖攻击？

**答案：**
依赖 `block.timestamp` 可能被矿工操纵（±15 秒），不适合关键逻辑。

```solidity
// 差：依赖精确时间戳
require(block.timestamp > deadline, "Expired");

// 好：使用区块号
require(block.number > deadlineBlock, "Expired");
```

### 28. tx.origin 和 msg.sender 的区别？

**答案：**
- **msg.sender**：直接调用者（可能是合约）
- **tx.origin**：交易的原始发送者（总是 EOA）

```solidity
// 危险：使用 tx.origin
function transfer() public {
    require(tx.origin == owner); // 可能被中间合约绕过
}

// 安全：使用 msg.sender
function transfer() public {
    require(msg.sender == owner);
}
```

### 29. 什么是前端运行攻击（Front-running）？

**答案：**
攻击者看到待处理的交易后，提交更高 Gas 价格的交易，让自己的交易先执行。

**防护方法：**
- 使用提交-揭示（commit-reveal）方案
- 使用私有内存池（如 Flashbots）
- 限制价格敏感操作的可见性

### 30. 如何安全地生成随机数？

**答案：**
区块链是确定性的，无法生成真正的随机数。

**常见方法：**
```solidity
// 方法 1：链上可预测（不安全）
uint random = uint(keccak256(abi.encodePacked(block.timestamp, block.difficulty)));

// 方法 2：Chainlink VRF（安全但需要费用）
// 使用 Chainlink VRF 获取可验证随机数

// 方法 3：提交-揭示方案
// 用户提交哈希，稍后揭示原始值
```

### 31. 什么是访问控制？如何实现？

**答案：**
访问控制限制只有授权地址可以执行特定操作。

```solidity
import "@openzeppelin/contracts/access/Ownable.sol";

contract AccessControl is Ownable {
    mapping(address => bool) public admins;
    
    modifier onlyAdmin() {
        require(admins[msg.sender] || msg.sender == owner(), "Not admin");
        _;
    }
    
    function addAdmin(address admin) public onlyOwner {
        admins[admin] = true;
    }
}
```

---

## 智能合约开发最佳实践

### 32. 什么是 Checks-Effects-Interactions 模式？

**答案：**
执行顺序：先检查（Checks），再更新状态（Effects），最后外部调用（Interactions）。

```solidity
function withdraw() public {
    // 1. Checks
    require(balances[msg.sender] > 0, "No balance");
    
    // 2. Effects
    uint amount = balances[msg.sender];
    balances[msg.sender] = 0;
    
    // 3. Interactions
    (bool success, ) = msg.sender.call{value: amount}("");
    require(success, "Transfer failed");
}
```

### 33. 如何处理错误？require、revert 和 assert 的区别？

**答案：**

| 函数 | Gas 退还 | 用途 | 示例 |
|------|---------|------|------|
| **require** | 是 | 输入验证、前置条件 | `require(x > 0, "x must be positive")` |
| **revert** | 是 | 复杂条件、自定义错误 | `if (x > 100) revert CustomError()` |
| **assert** | 否 | 内部错误、不变量 | `assert(balance >= 0)` |

```solidity
// 自定义错误（Gas 更省）
error InsufficientBalance(uint requested, uint available);

function withdraw(uint amount) public {
    if (balance < amount) {
        revert InsufficientBalance(amount, balance);
    }
}
```

### 34. 什么是库（Library）？如何使用？

**答案：**
库是部署一次、多处使用的代码，可以节省 Gas。

```solidity
library Math {
    function add(uint a, uint b) internal pure returns (uint) {
        return a + b;
    }
}

contract Example {
    using Math for uint;
    
    function calculate(uint a, uint b) public pure returns (uint) {
        return a.add(b); // 使用库函数
    }
}
```

**类型：**
- **内部库**：代码嵌入合约，不单独部署
- **外部库**：单独部署，多个合约共享

### 35. 如何实现升级模式？

**答案：**
常见模式：

**1. 代理模式（Proxy Pattern）**
```solidity
// 代理合约存储状态，逻辑合约可升级
contract Proxy {
    address public implementation;
    
    function upgrade(address newImpl) public {
        implementation = newImpl;
    }
    
    fallback() external {
        address impl = implementation;
        assembly {
            calldatacopy(0, 0, calldatasize())
            let result := delegatecall(gas(), impl, 0, calldatasize(), 0, 0)
            returndatacopy(0, 0, returndatasize())
            switch result
            case 0 { revert(0, returndatasize()) }
            default { return(0, returndatasize()) }
        }
    }
}
```

**2. 使用 OpenZeppelin Upgrades**
```solidity
// 使用 UUPS 或 Transparent Proxy
```

### 36. 如何测试智能合约？

**答案：**
- **单元测试**：使用 Hardhat、Foundry 或 Truffle
- **集成测试**：测试合约间交互
- **模糊测试**：使用 Echidna 或 Foundry Fuzz
- **形式化验证**：使用 Certora 或 Slither

```solidity
// Foundry 测试示例
contract TestExample {
    function testTransfer() public {
        MyToken token = new MyToken();
        token.transfer(address(1), 100);
        assert(token.balanceOf(address(1)) == 100);
    }
}
```

---

## 高级特性

### 37. 什么是委托调用（delegatecall）？

**答案：**
`delegatecall` 在调用者合约的上下文中执行被调用合约的代码，状态变量存储在调用者合约中。

```solidity
contract Library {
    function setValue(uint _value) public {
        // 这个函数会修改调用者合约的 storage
    }
}

contract Proxy {
    uint public value;
    address public library;
    
    function delegateCallSetValue(uint _value) public {
        (bool success, ) = library.delegatecall(
            abi.encodeWithSignature("setValue(uint256)", _value)
        );
        require(success);
    }
}
```

**用途：**
- 代理模式实现升级
- 库函数调用
- Gas 优化

### 38. 什么是 CREATE2？有什么优势？

**答案：**
`CREATE2` 允许在部署前计算合约地址，地址只依赖于：
- 创建者地址
- 盐值（salt）
- 字节码

```solidity
function deploy(bytes memory bytecode, uint salt) public returns (address) {
    address addr;
    assembly {
        addr := create2(0, add(bytecode, 0x20), mload(bytecode), salt)
    }
    return addr;
}

// 可以预先计算地址
function computeAddress(bytes memory bytecode, uint salt) public view returns (address) {
    bytes32 hash = keccak256(abi.encodePacked(
        bytes1(0xff),
        address(this),
        salt,
        keccak256(bytecode)
    ));
    return address(uint160(uint(hash)));
}
```

**优势：**
- 确定性地址
- 状态通道
- 反事实部署

### 39. 什么是内联汇编（Inline Assembly）？

**答案：**
内联汇编允许直接编写 EVM 字节码，用于：
- 优化 Gas
- 访问底层功能
- 实现复杂逻辑

```solidity
function assemblyExample(uint x, uint y) public pure returns (uint) {
    assembly {
        let result := add(x, y)
        mstore(0x0, result) // 存储到内存
        return(0x0, 32) // 返回 32 字节
    }
}
```

**注意：** 使用需谨慎，容易出错且难以维护。

### 40. 如何处理大数组？

**答案：**
大数组操作成本高，优化方法：

**1. 分页处理**
```solidity
function getItems(uint offset, uint limit) public view returns (Item[] memory) {
    // 只返回部分数据
}
```

**2. 使用映射代替数组**
```solidity
mapping(uint => Item) public items;
uint public itemCount;
```

**3. 链下索引**
```solidity
// 链上只存储必要数据，链下建立索引
event ItemCreated(uint indexed id, address indexed creator);
```

### 41. 什么是 EIP-712？如何实现签名验证？

**答案：**
EIP-712 定义了结构化数据签名标准，用于类型化数据签名。

```solidity
import "@openzeppelin/contracts/utils/cryptography/EIP712.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";

contract SignatureExample is EIP712 {
    using ECDSA for bytes32;
    
    constructor() EIP712("MyApp", "1") {}
    
    function verify(
        address signer,
        uint amount,
        bytes memory signature
    ) public view returns (bool) {
        bytes32 structHash = keccak256(abi.encode(
            keccak256("Transfer(address to,uint256 amount)"),
            msg.sender,
            amount
        ));
        bytes32 hash = _hashTypedDataV4(structHash);
        return hash.recover(signature) == signer;
    }
}
```

---

## 常见漏洞与防护

### 42. 什么是整数下溢/上溢？

**答案：**
当数值超出类型范围时发生溢出。

```solidity
// Solidity 0.8.0+ 自动检查
uint8 a = 255;
a += 1; // 自动 revert

// 0.7.x 需要 SafeMath
using SafeMath for uint256;
uint256 a = a.add(1);
```

### 43. 什么是未初始化存储指针？

**答案：**
结构体或数组的存储指针必须明确指定位置。

```solidity
// 错误
struct Data {
    uint value;
}

function bad() public {
    Data memory d; // 这是 memory，不是 storage
    d.value = 100; // 修改 memory 不会影响 storage
}

// 正确
function good() public {
    Data storage d = data; // 明确指定 storage 位置
    d.value = 100;
}
```

### 44. 什么是函数选择器冲突？

**答案：**
不同函数可能产生相同的 4 字节选择器。

```solidity
// 这两个函数的选择器可能冲突
function transfer(address to, uint amount) public {}
function transfer(address to, uint256 amount) public {}
```

**防护：** 使用不同的函数名或参数类型。

### 45. 什么是短地址攻击？

**答案：**
攻击者发送不完整的地址（末尾补零），导致参数解析错误。

**防护：** Solidity 0.5.0+ 已修复，编译器会检查地址长度。

### 46. 如何防止 DoS 攻击？

**答案：**
- **限制循环次数**：避免无界循环
- **使用映射代替数组**：O(1) 查找
- **分页处理**：大数组分批处理
- **Gas Limit**：设置合理的 Gas 限制

```solidity
// 差：无界循环
function processAll() public {
    for (uint i = 0; i < items.length; i++) {
        // 可能 Gas 不足
    }
}

// 好：限制处理数量
function processBatch(uint limit) public {
    uint count = 0;
    for (uint i = 0; i < items.length && count < limit; i++) {
        // 处理
        count++;
    }
}
```

### 47. 什么是闪电贷攻击？

**答案：**
利用闪电贷在同一交易中借入大量资金进行套利或攻击。

**防护：**
- 检查价格变化
- 使用时间加权平均价格（TWAP）
- 限制单次交易金额

### 48. 如何安全地处理 ETH 转账？

**答案：**

```solidity
// 方法 1：使用 transfer（有 Gas 限制，可能失败）
payable(recipient).transfer(amount);

// 方法 2：使用 send（返回 bool，需要检查）
bool success = payable(recipient).send(amount);
require(success, "Transfer failed");

// 方法 3：使用 call（推荐，但需防护重入）
(bool success, ) = recipient.call{value: amount}("");
require(success, "Transfer failed");

// 方法 4：使用 OpenZeppelin Address.sendValue
Address.sendValue(payable(recipient), amount);
```

### 49. 什么是权限提升漏洞？

**答案：**
合约权限控制不当，允许未授权操作。

```solidity
// 漏洞：任何人都可以成为 owner
function becomeOwner() public {
    owner = msg.sender;
}

// 正确：只有当前 owner 可以转移
function transferOwnership(address newOwner) public onlyOwner {
    require(newOwner != address(0), "Invalid address");
    owner = newOwner;
}
```

### 50. 如何安全地使用外部调用？

**答案：**

```solidity
// 1. 检查返回值
(bool success, bytes memory data) = target.call{value: amount}("");
require(success, "Call failed");

// 2. 使用低级别调用时验证合约存在
require(target.code.length > 0, "Target is not a contract");

// 3. 防护重入攻击
modifier nonReentrant() {
    require(!locked, "Reentrant call");
    locked = true;
    _;
    locked = false;
}

// 4. 限制外部调用的 Gas
target.call{value: amount, gas: 50000}("");
```

### 51. 智能合约审计要点有哪些？

**答案：**

**1. 安全性检查**
- 重入攻击
- 整数溢出
- 访问控制
- 输入验证

**2. Gas 优化**
- 存储布局
- 循环优化
- 函数选择

**3. 代码质量**
- 代码规范
- 注释完整性
- 错误处理

**4. 业务逻辑**
- 业务规则正确性
- 边界条件
- 异常情况处理

**5. 工具使用**
- Slither（静态分析）
- Mythril（符号执行）
- Echidna（模糊测试）

---

## 总结

Solidity 智能合约开发需要深入理解：
- **语言特性**：数据类型、函数、继承等
- **Gas 优化**：存储布局、算法选择等
- **安全性**：常见漏洞和防护措施
- **最佳实践**：代码规范和设计模式

持续学习新的 EIP 标准和工具，保持对安全性的高度警惕，是成为优秀 Solidity 开发者的关键。

