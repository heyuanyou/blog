---
title: "Java 高频面试题（含 SSM）"
date: 2026-09-22
main: "面试"
sub: ["java", "ssm", "spring", "mybatis", "jvm", "backend"]
summary: "按面试口径整理 Java 高频问题，覆盖集合、并发、JVM、Java 8 新特性，并专门补充 SSM（Spring / Spring MVC / MyBatis）高频考点。"
---

# Java 高频面试题（含 SSM）

这篇文章按面试问答形式整理，前半部分是 Java 语言和 JVM 高频题，后半部分专门整理 SSM（Spring + Spring MVC + MyBatis）相关高频题，尽量用"能直接说出口"的方式覆盖考点。

---

## 1. 面向对象基础怎么答？

### Q: 面向对象三大特性是什么？
**标准回答：**

1. **封装**：把数据和操作数据的方法绑定在一起，对外隐藏实现细节
2. **继承**：子类复用父类的属性和行为，同时可以扩展
3. **多态**：同一个方法调用，因为对象的实际类型不同而表现出不同行为

### Q: 多态是怎么实现的？
Java 里多态主要靠**方法重写（override）+ 动态绑定**实现。运行时 JVM 会根据对象的实际类型去查找方法表，决定调用哪个具体实现，这个过程叫**虚方法调用**。

### Q: 重载和重写的区别？
**标准回答：**

1. **重载（Overload）**：同一个类里，方法名相同，参数列表不同，属于**编译期**绑定
2. **重写（Override）**：子类重新实现父类方法，方法签名保持一致，属于**运行期**绑定

### Q: 接口和抽象类的区别？
常见抓几个维度：

1. 抽象类可以有构造方法，接口不行
2. 一个类只能继承一个抽象类，但可以实现多个接口
3. Java 8 之后接口可以有 `default` 方法和静态方法，边界变得模糊了
4. 抽象类更偏"是什么"的继承关系，接口更偏"能做什么"的能力声明

---

## 2. == 和 equals()、hashCode() 怎么答？

### Q: == 和 equals() 有什么区别？
**标准回答：**

1. `==` 对基本类型比较的是值，对引用类型比较的是**内存地址**
2. `equals()` 默认（Object 类）也是比较地址，但很多类（如 String、Integer、集合里的自定义对象）会重写它来比较**内容**

### Q: 为什么重写 equals() 一定要重写 hashCode()？
因为 `HashMap`、`HashSet` 这类基于哈希的容器，判断两个对象是否"相等"依赖两步：

1. 先比较 `hashCode()`，如果不同直接认为不是同一个 key
2. 如果 `hashCode()` 相同再用 `equals()` 精确比较

如果只重写 `equals()` 不重写 `hashCode()`，就会出现逻辑上相等的两个对象、`hashCode()` 却不同，导致放进 `HashMap` 后查不出来。

### Q: String 为什么是不可变的？有什么好处？
**面试口径：**

String 内部用 `final` 数组存储字符内容，一旦创建就不能修改。好处主要有：

1. 可以安全地被多线程共享，不用加锁
2. 可以支撑**字符串常量池**，相同内容的字符串可以复用，节省内存
3. 作为 `HashMap` 的 key 更安全，哈希值可以缓存不会变

---

## 3. 集合框架高频题

### Q: ArrayList 和 LinkedList 的区别？
**标准回答：**

1. **底层结构**：ArrayList 是动态数组，LinkedList 是双向链表
2. **随机访问**：ArrayList 是 O(1)，LinkedList 是 O(n)
3. **插入删除**：ArrayList 中间插入删除要挪动元素，平均 O(n)；LinkedList 头尾操作是 O(1)，中间插入删除也要先遍历找到位置

### Q: ArrayList 扩容机制是怎样的？
默认容量是 10，扩容时按**原容量的 1.5 倍**（`oldCapacity + oldCapacity >> 1`）计算新容量，然后用 `Arrays.copyOf` 把数据拷贝到新数组。

### Q: HashMap 的底层结构是怎样的？
JDK 8 之后是**数组 + 链表 + 红黑树**：

1. 默认数组长度 16，负载因子 0.75
2. 每个数组位置（桶）存的是链表
3. 当某个桶里链表长度**超过 8**，并且数组长度**大于等于 64** 时，链表会转成**红黑树**，提升查找效率

### Q: 为什么链表长度超过 8 才树化，不是一开始就用树？
因为链表在长度较短时，遍历成本本身就不高，红黑树的维护成本（插入、旋转）反而更高。只有链表变长、退化成近似 O(n) 查找时，红黑树 O(log n) 的优势才划算。

### Q: HashMap 是怎么解决哈希冲突的？
主要靠**链地址法**：哈希值相同的元素放到同一个桶的链表（或红黑树）里。另外 JDK 8 对 `hashCode()` 做了**扰动函数**处理（高16位异或低16位），让哈希分布更均匀，减少冲突。

### Q: HashMap 的扩容机制是怎样的？
当元素个数超过 `容量 × 负载因子`（默认 16 × 0.75 = 12）时触发扩容，容量翻倍为原来的 2 倍，并重新计算每个元素在新数组里的位置（rehash）。

### Q: HashMap 在多线程下有什么问题？
JDK 7 下扩容时链表可能形成**环形链表**，导致死循环；JDK 8 虽然改进了扩容逻辑，但依然**不是线程安全**的，多线程并发写可能导致数据覆盖或丢失，生产环境要用 `ConcurrentHashMap`。

### Q: ConcurrentHashMap 是怎么保证线程安全的？
**标准回答（JDK 8 版本）：**

1. 不再使用 JDK 7 的**分段锁（Segment）**
2. 改成对每个**桶的头节点**加锁（`synchronized`），锁粒度更细
3. 配合 `CAS` 操作处理无冲突的插入场景
4. 树化逻辑和 HashMap 类似

### Q: HashMap 和 Hashtable 的区别？
1. Hashtable 所有方法都用 `synchronized` 修饰，性能差，现在基本不用
2. HashMap 允许 key 和 value 为 `null`，Hashtable 不允许
3. 并发场景现在推荐用 `ConcurrentHashMap`

---

## 4. 异常处理怎么答？

### Q: Checked Exception 和 Unchecked Exception 的区别？
**标准回答：**

1. **Checked Exception**（如 `IOException`）：编译期强制要求处理，要么 `try-catch` 要么 `throws` 声明
2. **Unchecked Exception**（`RuntimeException` 及其子类，如 `NullPointerException`）：编译期不强制处理，通常代表编程错误

### Q: final、finally、finalize 的区别？
1. `final`：修饰符，表示不可变、不可继承、不可重写
2. `finally`：`try-catch` 语句块的一部分，通常用于释放资源，一般都会执行
3. `finalize`：Object 的方法，GC 回收对象前的回调，现在已不推荐依赖，JDK 9 后标记废弃

### Q: try-catch-finally 里 finally 一定会执行吗？
绝大多数情况会执行，但也有例外：

1. `try` 之前程序就崩溃（如 JVM 崩溃、`System.exit()`）
2. 线程被强制终止

---

## 5. 多线程与并发高频题

### Q: 创建线程有哪几种方式？
常见能说出：

1. 继承 `Thread` 类
2. 实现 `Runnable` 接口
3. 实现 `Callable` 接口（配合 `FutureTask` 拿返回值）
4. 通过线程池（`ExecutorService`）

### Q: synchronized 和 Lock（ReentrantLock）的区别？
**标准回答：**

1. `synchronized` 是 JVM 层面的关键字，`Lock` 是 JUC 包里的接口实现
2. `synchronized` 无法中断等待、无法设置超时；`Lock` 可以（`tryLock`、`lockInterruptibly`）
3. `Lock` 支持**公平锁**，`synchronized` 只有非公平锁
4. `synchronized` 会自动释放锁，`Lock` 需要手动在 `finally` 里 `unlock()`
5. JDK 6 之后 `synchronized` 做了大量优化（偏向锁、轻量级锁、锁膨胀），性能差距已经不大

### Q: volatile 关键字的作用是什么？
**标准回答：**

1. 保证**可见性**：一个线程修改了变量，其他线程能立刻看到最新值（禁止本地缓存）
2. 禁止**指令重排序**：通过内存屏障，保证有序性
3. **不保证原子性**，比如 `i++` 这种复合操作用 `volatile` 依然不是线程安全的

### Q: 什么是 CAS？有什么问题？
CAS（Compare And Swap）是一种乐观锁思路：比较内存里的值和预期值，相同才更新，否则重试。JUC 里很多原子类（`AtomicInteger`）和并发容器都基于它。

常见问题：

1. **ABA 问题**：值从 A 改成 B 又改回 A，CAS 看不出变化，可以用版本号（`AtomicStampedReference`）解决
2. **自旋开销**：高并发下 CAS 失败会不断重试，消耗 CPU
3. 只能保证**单个变量**的原子性

### Q: 什么是 AQS？
AQS（AbstractQueuedSynchronizer）是 JUC 并发包的核心基础框架，`ReentrantLock`、`CountDownLatch`、`Semaphore` 等都是基于它实现的。核心思路是：

1. 用一个 `volatile int state` 表示同步状态
2. 用一个 **FIFO 等待队列** 管理获取锁失败的线程
3. 子类通过重写 `tryAcquire`/`tryRelease` 等方法定义具体的加锁语义

### Q: 线程池的核心参数有哪些？
`ThreadPoolExecutor` 的构造参数，高频必背：

1. **corePoolSize**：核心线程数
2. **maximumPoolSize**：最大线程数
3. **keepAliveTime**：空闲线程存活时间
4. **workQueue**：任务队列
5. **threadFactory**：线程创建工厂
6. **RejectedExecutionHandler**：拒绝策略

### Q: 线程池的任务处理流程是怎样的？
**标准回答：**

1. 线程数没达到 `corePoolSize`，直接创建新线程执行
2. 达到 `corePoolSize` 后，新任务进入**队列**排队
3. 队列满了，且线程数没达到 `maximumPoolSize`，创建新线程执行
4. 线程数也达到上限了，触发**拒绝策略**

### Q: 常见拒绝策略有哪些？
1. `AbortPolicy`：直接抛异常（默认）
2. `CallerRunsPolicy`：让提交任务的线程自己执行
3. `DiscardPolicy`：直接丢弃，不抛异常
4. `DiscardOldestPolicy`：丢弃队列里最老的任务，再尝试提交

### Q: 为什么阿里巴巴规范不推荐用 Executors 创建线程池？
因为 `Executors` 提供的几种默认线程池（如 `newFixedThreadPool`、`newCachedThreadPool`）内部队列或线程数容易配置成**无界**，在高并发场景下可能导致**内存溢出**。建议直接用 `ThreadPoolExecutor` 显式指定每个参数。

### Q: 什么是死锁？怎么排查？
死锁通常是多个线程互相持有对方需要的锁，形成循环等待。排查手段：

1. `jstack` 打印线程堆栈，看是否有 `Found one Java-level deadlock` 提示
2. 分析线程状态是否为 `BLOCKED` 并且互相等待对方锁

预防思路：固定加锁顺序、缩小锁范围、加锁超时（用 `tryLock`）。

---

## 6. JVM 高频题

### Q: JVM 运行时内存区域有哪些？
**标准回答：**

1. **堆（Heap）**：存对象实例，所有线程共享，是 GC 的主要区域
2. **虚拟机栈**：每个线程私有，存局部变量表、操作数栈、方法出口等
3. **本地方法栈**：为 Native 方法服务
4. **程序计数器**：记录当前线程执行到的字节码位置，线程私有
5. **方法区 / 元空间（Metaspace）**：存类信息、常量、静态变量，JDK 8 后用**元空间**（直接内存）替代了永久代

### Q: 为什么 JDK 8 要用元空间替代永久代？
永久代大小固定、容易 `OutOfMemoryError: PermGen space`；元空间使用**本地内存**，默认没有固定上限（受物理内存限制），更适合动态类加载（比如大量使用 CGLIB 动态代理的场景）。

### Q: 对象是怎么在堆里分配和回收的？
一般思路：

1. 新对象**优先在 Eden 区**分配
2. Eden 区满了触发 **Minor GC**，存活对象移到 Survivor 区
3. 对象在 Survivor 区经历多次 GC（默认年龄阈值 15）还存活，会晋升到**老年代**
4. 老年代满了触发 **Major/Full GC**

### Q: 常见的垃圾回收算法有哪些？
1. **标记-清除**：先标记存活对象，再清除未标记对象，缺点是产生内存碎片
2. **标记-整理**：标记后把存活对象往一端移动，再清理边界外内存，解决了碎片问题但成本更高
3. **复制算法**：把内存分两块，每次只用一块，回收时把存活对象复制到另一块，适合**存活率低**的新生代

### Q: 常见的垃圾收集器有哪些？怎么选？
高频能说出：

1. **Serial**：单线程，适合客户端、小内存场景
2. **Parallel Scavenge / Parallel Old**：多线程，重视**吞吐量**
3. **CMS**：以**最短停顿时间**为目标，并发标记清除，但会产生内存碎片，JDK 9 后已废弃
4. **G1**：分Region管理堆，可预测停顿时间，JDK 9 后成为默认收集器，适合大堆场景
5. **ZGC / Shenandoah**：追求**超低停顿**（毫秒级），适合超大堆场景

### Q: 什么是 STW（Stop The World）？
GC 执行某些阶段（如标记）时，需要暂停所有用户线程，避免对象引用关系在标记过程中发生变化，这个暂停就叫 STW。收集器演进的一大方向就是**尽量缩短 STW 时间**。

### Q: 什么情况下对象会被判定为垃圾（可回收）？
主流是**可达性分析算法**：从一系列 **GC Roots**（如虚拟机栈的局部变量、方法区的静态变量引用等）出发，沿引用链向下搜索，不可达的对象就是可回收对象。

### Q: 类加载的双亲委派机制是什么？
**标准回答：**

一个类加载器收到加载请求时，不会自己先尝试加载，而是先把请求**委派给父类加载器**，一直递归到最顶层的启动类加载器。只有父加载器反馈"无法加载"时，子加载器才会自己尝试。

### Q: 双亲委派机制有什么好处？
1. 避免**类的重复加载**
2. 保证核心类库（如 `java.lang.Object`）不会被自定义类加载器随意替换，保证安全性

### Q: 线上服务频繁 Full GC 怎么排查？
一般思路：

1. 先用 `jstat -gc` 或监控平台看 GC 频率和耗时趋势
2. 用 `jmap -dump` 导出堆快照，配合 MAT / VisualVM 分析对象占用
3. 排查是否存在**内存泄漏**（如集合类持续增长未释放、缓存没有过期策略）
4. 检查是否有大对象、大数组频繁创建
5. 结合业务代码定位具体调用链

---

## 7. Java 8+ 新特性

### Q: Lambda 表达式的本质是什么？
Lambda 本质上是**函数式接口**（只有一个抽象方法的接口，如 `Runnable`、`Comparator`）的一种简洁实现方式，编译器会在背后生成对应的匿名实现（底层基于 `invokedynamic` 和方法句柄）。

### Q: Stream 流的核心思想是什么？
把集合操作抽象成**声明式、链式**的数据处理管道，分成三类操作：

1. **数据源**：如 `list.stream()`
2. **中间操作**：`filter`、`map`、`sorted` 等，**惰性求值**，不会立刻执行
3. **终止操作**：`collect`、`forEach`、`reduce` 等，触发真正的计算

### Q: Optional 的作用是什么？主要为了解决什么问题？
`Optional` 是一个容器类，用来显式表达"值可能不存在"，主要目的是减少 `NullPointerException`，让调用方在编译期就意识到需要处理"空"的情况，而不是运行时才踩坑。

---

## 8. SSM 高频题：Spring 核心

### Q: 什么是 IOC？什么是 DI？
**标准回答：**

1. **IOC（控制反转）**是一种设计思想：对象的创建、依赖关系的管理，从代码里"主动 new"变成交给容器统一管理
2. **DI（依赖注入）**是 IOC 的一种具体实现方式：容器在创建 Bean 时，自动把它依赖的其他 Bean"注入"进来

### Q: Spring Bean 的生命周期是怎样的？
一个相对完整的顺序：

1. 实例化（调用构造方法）
2. 属性赋值（依赖注入）
3. 执行 `Aware` 接口回调（如 `BeanNameAware`）
4. 执行 `BeanPostProcessor` 的 `postProcessBeforeInitialization`
5. 执行 `@PostConstruct` / `InitializingBean.afterPropertiesSet()` / 自定义 `init-method`
6. 执行 `BeanPostProcessor` 的 `postProcessAfterInitialization`（**AOP 代理通常在这一步生成**）
7. Bean 可以正常使用
8. 容器关闭时执行 `@PreDestroy` / `DisposableBean.destroy()`

### Q: Spring 是怎么解决循环依赖的？
**标准回答：**

针对**单例、setter 注入**的循环依赖，Spring 用**三级缓存**解决：

1. **一级缓存**：完全初始化好的单例对象
2. **二级缓存**：提前暴露的、实例化但还未完全初始化的对象
3. **三级缓存**：存放对象工厂（`ObjectFactory`），用于生成提前暴露的代理对象

当 A 依赖 B、B 又依赖 A 时，A 实例化后先放入三级缓存暴露自己，B 创建时从三级缓存拿到 A 的早期引用完成注入，从而打破循环。

### Q: 为什么构造器注入没法解决循环依赖？
因为构造器注入要求在**实例化阶段**就把依赖准备好，而这时候对象还没创建出来，没有"提前暴露的半成品"可以给对方引用，所以三级缓存这套机制对构造器注入无效。

### Q: Spring AOP 的实现原理是什么？
基于**动态代理**：

1. 如果目标类**实现了接口**，默认用 **JDK 动态代理**（基于接口生成代理类）
2. 如果目标类**没有实现接口**，用 **CGLIB**（通过继承目标类、生成子类字节码实现代理）
3. Spring Boot 2.x 之后默认统一用 **CGLIB**（除非显式配置）

### Q: AOP 常见的应用场景有哪些？
日志记录、权限校验、事务管理、缓存处理、限流熔断等**横切关注点**，核心价值是把这些和业务逻辑无关的逻辑从业务代码里抽离出来。

### Q: Spring 事务的传播机制有哪些？
高频能说出几个核心的：

1. **REQUIRED**（默认）：有事务就加入，没有就新建
2. **REQUIRES_NEW**：无论有没有事务，都新建一个独立事务，原事务挂起
3. **SUPPORTS**：有事务就加入，没有就以非事务方式执行
4. **NESTED**：嵌套事务，基于 Savepoint，外层回滚会带动内层回滚，内层回滚不一定影响外层

### Q: @Transactional 有哪些常见失效场景？
面试高频坑点：

1. 方法**不是 public**（Spring AOP 代理限制）
2. **同一个类内部**方法互相调用（`this.method()` 不走代理，事务不生效）
3. 异常被 `try-catch` **吞掉**，没有再抛出
4. 抛出的是**受检异常**，但没配置 `rollbackFor`（默认只回滚 `RuntimeException`）
5. 数据库引擎本身**不支持事务**（如 MyISAM）
6. 方法上加了 `@Transactional`，但类没有被 Spring 管理（没交给容器）

### Q: Spring 事务失效的根本原因是什么？
本质上都是绕过了 Spring 生成的**代理对象**去调用方法，事务逻辑是通过代理里的拦截器实现的，只要没走代理，事务的前置开启、后置提交/回滚逻辑就不会被触发。

---

## 9. SSM 高频题：Spring MVC

### Q: Spring MVC 的请求处理流程是怎样的？
**标准回答（核心链路）：**

1. 请求先到 **DispatcherServlet**（前端控制器）
2. `DispatcherServlet` 调用 **HandlerMapping** 找到对应的 Controller 方法（Handler）
3. 通过 **HandlerAdapter** 去实际调用这个方法
4. Controller 方法执行，返回结果（如 `ModelAndView` 或直接是数据）
5. 如果返回视图名，交给 **ViewResolver** 解析成具体的 View
6. 渲染视图，返回响应给客户端

### Q: DispatcherServlet 是什么角色？
它是 Spring MVC 的**前端控制器（Front Controller）**，所有请求的统一入口，负责调度各个组件协同完成一次请求处理，本身不处理具体业务逻辑。

### Q: @RequestMapping 和 @GetMapping 有什么关系？
`@GetMapping` 等价于 `@RequestMapping(method = RequestMethod.GET)` 的组合注解，是 Spring 4.3 之后提供的语法糖，让代码更简洁、语义更清晰。

### Q: @RequestBody 和 @ResponseBody 的作用？
1. `@RequestBody`：把请求体（通常是 JSON）反序列化成 Java 对象
2. `@ResponseBody`：把方法返回的 Java 对象序列化成 JSON 写入响应体
它们的底层都依赖 `HttpMessageConverter`（默认常用 Jackson）。

### Q: 拦截器（Interceptor）和过滤器（Filter）的区别？
**标准回答：**

1. **所属层面不同**：Filter 是 Servlet 规范的一部分，Interceptor 是 Spring MVC 自己的机制
2. **生效范围不同**：Filter 可以拦截所有请求（包括静态资源），Interceptor 只拦截进入 `DispatcherServlet` 的请求
3. **能力不同**：Interceptor 可以拿到 Handler 信息（比如具体调用哪个 Controller 方法），能更细粒度地做权限、日志处理；Filter 拿不到

---

## 10. SSM 高频题：MyBatis

### Q: MyBatis 的核心工作原理是什么？
**标准回答（简化链路）：**

1. 加载 `mybatis-config.xml` 和各个 Mapper 映射文件，解析成内存里的配置对象
2. 通过 `SqlSessionFactory` 创建 `SqlSession`
3. `SqlSession` 内部通过 **JDK 动态代理**为 Mapper 接口生成代理对象
4. 调用 Mapper 方法时，代理对象根据方法签名找到对应的 SQL 语句，执行 JDBC 操作
5. 对结果集做**对象关系映射（ORM）**，转换成 Java 对象返回

### Q: MyBatis 里 #{} 和 ${} 有什么区别？
**这是高频送分题也是高频事故题：**

1. `#{}` 会被预编译成 **JDBC 的占位符（?）**，参数以**预编译**方式传入，能有效防止 **SQL 注入**
2. `${}` 是**字符串拼接**，直接把值替换进 SQL 文本，存在 SQL 注入风险
3. 实际开发里绝大多数场景优先用 `#{}`，`${}` 只用于**表名、字段名、排序字段**这类无法用占位符传递的场景，且要做好校验

### Q: MyBatis 的一级缓存和二级缓存分别是什么？
**标准回答：**

1. **一级缓存**：`SqlSession` 级别，默认开启，同一个 `SqlSession` 内相同查询会走缓存；`SqlSession` 关闭或执行增删改后缓存会失效
2. **二级缓存**：`Mapper（namespace）` 级别，需要手动开启，可以跨 `SqlSession` 共享，默认实现基于内存的 `HashMap`，也可以接入 Redis 等外部缓存

### Q: MyBatis 二级缓存有什么使用注意点？
1. 对**多表关联、频繁更新**的数据要慎用，容易出现脏数据
2. 需要对象实现 `Serializable`
3. 分布式部署下默认的本地缓存实现无法多实例共享，需要接入分布式缓存方案

### Q: MyBatis 的延迟加载是怎么实现的？
基于**动态代理**（默认 CGLIB 或 Javassist）：查询主对象时先不加载关联对象，只有真正调用关联对象的 getter 方法触发代理逻辑时，才去执行对应的 SQL 加载关联数据。

### Q: MyBatis 中 resultMap 和 resultType 有什么区别？
1. `resultType`：直接指定返回类型，要求**字段名和属性名**能自动对应（或者用别名对齐）
2. `resultMap`：可以显式配置字段和属性的映射关系，支持**一对一、一对多**这类复杂关联映射，更灵活

### Q: MyBatis 是怎么防止 SQL 注入的？
核心还是**优先使用 `#{}` 预编译参数**；对于必须拼接的字段（排序、表名等），要做白名单校验，避免直接拼接用户输入。

### Q: MyBatis 和 Hibernate 的区别怎么答？
常见对比维度：

1. **SQL 控制粒度**：MyBatis 是"半自动"，SQL 需要自己写，控制力强；Hibernate 是"全自动" ORM，SQL 自动生成，开发效率高但优化空间受限
2. **学习和上手成本**：MyBatis 更贴近 SQL，学习成本低；Hibernate 概念（如 Session、一级二级缓存、懒加载策略）更多，上手曲线更陡
3. **适用场景**：复杂查询、性能要求高、SQL 需要精细调优的场景更倾向 MyBatis；简单 CRUD、快速开发场景 Hibernate 效率更高

---

## 11. SSM 高频题最后怎么总结？

### Q: 如果让我 1 分钟总结 SSM，我会怎么说？
我一般会这样答：

> SSM 是 Spring + Spring MVC + MyBatis 的组合，各司其职：Spring 负责 IOC/DI 和 AOP，是整个体系的容器和粘合剂；Spring MVC 负责 Web 层请求分发，核心是 DispatcherServlet 统一调度 HandlerMapping、HandlerAdapter、ViewResolver；MyBatis 负责持久层，核心是通过动态代理把 Mapper 接口和 SQL 语句绑定起来，同时提供一级/二级缓存和延迟加载能力。面试高频坑点集中在 Bean 生命周期和循环依赖、AOP 动态代理选择、事务传播机制和 @Transactional 失效场景、DispatcherServlet 请求流程，以及 MyBatis 的 #{} 和 ${} 区别。把这几块讲清楚，SSM 面试基本就有主线了。

---

如果你准备的是 Java 后端面试，高频题通常绕不开这些点：

1. 面向对象三大特性、重载与重写
2. == 与 equals/hashCode、String 不可变性
3. HashMap 底层结构、扩容与树化、ConcurrentHashMap 线程安全实现
4. synchronized 与 Lock、volatile、CAS、AQS
5. 线程池核心参数、拒绝策略、Executors 的坑
6. JVM 内存结构、垃圾回收算法与收集器、双亲委派
7. Lambda 与 Stream 的本质
8. Spring Bean 生命周期与循环依赖三级缓存、AOP 动态代理原理
9. Spring 事务传播机制与 @Transactional 失效场景
10. DispatcherServlet 请求处理流程、拦截器与过滤器的区别
11. MyBatis 工作原理、#{} 与 ${}、一级二级缓存、延迟加载

这些问题能讲清楚，Java + SSM 面试基本就有框架了。
