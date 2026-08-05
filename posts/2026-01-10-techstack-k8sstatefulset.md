---
title: "Kubernetes StatefulSet：有状态应用管理详解"
date: 2026-01-10
main: "分布式"
sub: ["kubernetes", "statefulset", "stateful", "container-orchestration"]
summary: "Kubernetes StatefulSet 全面指南，深入解析有状态应用管理、稳定的网络标识、有序部署、持久化存储等核心特性，涵盖从基础到高级的各个方面"
---

# Kubernetes StatefulSet：有状态应用管理详解

## 目录

- [基础概念](#基础概念)
- [StatefulSet vs Deployment](#statefulset-vs-deployment)
- [核心特性](#核心特性)
- [配置详解](#配置详解)
- [网络标识与 Service](#网络标识与-service)
- [持久化存储](#持久化存储)
- [扩缩容](#扩缩容)
- [更新策略](#更新策略)
- [使用场景](#使用场景)
- [最佳实践](#最佳实践)
- [常见问题与解决方案](#常见问题与解决方案)
- [高级特性](#高级特性)

---

## 基础概念

### 1. 什么是 StatefulSet？它有哪些特点？

**答案：**

StatefulSet 是 Kubernetes 中用于管理有状态应用的工作负载资源，提供了稳定的网络标识、有序部署和持久化存储等特性。

**主要特点：**

- **稳定的网络标识**：每个 Pod 有唯一且稳定的网络标识
- **有序部署**：按顺序创建和删除 Pod
- **有序扩缩容**：按顺序进行扩缩容操作
- **持久化存储**：每个 Pod 有独立的持久化存储
- **有序更新**：支持有序的滚动更新
- **稳定的存储**：Pod 重建后仍能访问相同的存储

**应用场景：**

- **数据库**：MySQL、PostgreSQL、MongoDB 等
- **消息队列**：Kafka、RabbitMQ 等
- **分布式系统**：Elasticsearch、ZooKeeper 等
- **有状态服务**：需要稳定标识和持久化存储的应用

### 2. StatefulSet 的架构是什么？

**答案：**

StatefulSet 的架构：

```
StatefulSet
  ├─ Pod 0 (web-0)
  │   ├─ 网络标识：web-0.web.default.svc.cluster.local
  │   ├─ 存储：web-data-web-0
  │   └─ 有序索引：0
  ├─ Pod 1 (web-1)
  │   ├─ 网络标识：web-1.web.default.svc.cluster.local
  │   ├─ 存储：web-data-web-1
  │   └─ 有序索引：1
  └─ Pod 2 (web-2)
      ├─ 网络标识：web-2.web.default.svc.cluster.local
      ├─ 存储：web-data-web-2
      └─ 有序索引：2

Headless Service
  └─ 提供稳定的 DNS 解析
```

**核心组件：**

1. **StatefulSet Controller**：管理 Pod 的生命周期
2. **Headless Service**：提供稳定的网络标识
3. **PersistentVolumeClaim**：提供持久化存储
4. **Pod**：有状态的 Pod 实例

---

## StatefulSet vs Deployment

### 3. StatefulSet 和 Deployment 的主要区别？

**答案：**

| 特性 | StatefulSet | Deployment |
|------|------------|------------|
| **网络标识** | 稳定（web-0, web-1） | 随机（web-xxx） |
| **存储** | 每个 Pod 独立存储 | 共享或临时存储 |
| **部署顺序** | 有序（0→1→2） | 并行 |
| **删除顺序** | 逆序（2→1→0） | 并行 |
| **扩缩容** | 有序 | 并行 |
| **更新策略** | 有序滚动更新 | 滚动更新 |
| **适用场景** | 有状态应用 | 无状态应用 |
| **DNS 解析** | 稳定的 DNS 名称 | 通过 Service 负载均衡 |

**网络标识对比：**

```yaml
# Deployment
Pod 名称：web-7d4b8c9f5-abc12
DNS：web.default.svc.cluster.local（负载均衡）

# StatefulSet
Pod 名称：web-0, web-1, web-2
DNS：web-0.web.default.svc.cluster.local（直接访问）
```

**存储对比：**

```yaml
# Deployment
- 所有 Pod 共享存储（ReadWriteMany）
- 或使用临时存储（emptyDir）

# StatefulSet
- 每个 Pod 有独立的存储（ReadWriteOnce）
- Pod 重建后仍能访问相同存储
```

### 4. 什么时候使用 StatefulSet？

**答案：**

**使用 StatefulSet 的场景：**

1. **需要稳定的网络标识**
   - 应用依赖 Pod 的稳定名称
   - 需要直接访问特定 Pod

2. **需要持久化存储**
   - 每个 Pod 需要独立存储
   - Pod 重建后需要访问相同数据

3. **需要有序部署**
   - 主从复制（Master-Slave）
   - 需要按顺序初始化

4. **需要有序扩缩容**
   - 集群需要按顺序加入节点
   - 需要优雅的缩容

**示例场景：**

- **数据库集群**：MySQL 主从、MongoDB 副本集
- **消息队列**：Kafka Broker 集群
- **分布式存储**：Elasticsearch 集群
- **有状态服务**：需要会话保持的应用

---

## 核心特性

### 5. 什么是稳定的网络标识？

**答案：**

StatefulSet 为每个 Pod 提供稳定的网络标识，包括稳定的 Pod 名称和 DNS 名称。

**重要说明：**

⚠️ **StatefulSet 不保证 Pod IP 地址固定！**

- **Pod IP 是动态分配的**：即使 StatefulSet 也不能保证 Pod IP 不变
- **稳定的网络标识 = 稳定的 DNS 名称**：通过 DNS 名称访问，而不是 IP
- **Pod 重建后 IP 可能改变**：但 DNS 名称保持不变

**Pod 命名规则：**

```
<statefulset-name>-<ordinal>
```

**示例：**
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web
spec:
  replicas: 3
  # Pod 名称：web-0, web-1, web-2
```

**DNS 名称：**

```
<pod-name>.<service-name>.<namespace>.svc.cluster.local
```

**示例：**
```
web-0.web.default.svc.cluster.local
web-1.web.default.svc.cluster.local
web-2.web.default.svc.cluster.local
```

**IP vs DNS 对比：**

```bash
# Pod IP（可能变化）
web-0: 10.244.1.10  # 重建后可能变成 10.244.2.15

# DNS 名称（稳定不变）
web-0.web.default.svc.cluster.local  # 始终解析到 web-0 的当前 IP
```

**为什么使用 DNS 而不是 IP？**

- **IP 会变化**：Pod 重建、节点迁移都会导致 IP 变化
- **DNS 稳定**：DNS 名称始终指向正确的 Pod，即使 IP 变化
- **服务发现**：通过 DNS 实现服务发现，不依赖 IP

**使用示例：**
```python
# 应用代码中可以使用稳定的 DNS 名称
import socket

# 获取当前 Pod 的序号
hostname = socket.gethostname()  # web-0
ordinal = int(hostname.split('-')[-1])

# 访问其他 Pod
for i in range(3):
    if i != ordinal:
        peer = f"web-{i}.web.default.svc.cluster.local"
        # 连接到 peer
```

### 6. 有序部署是如何工作的？

**答案：**

StatefulSet 按照索引顺序创建和删除 Pod，确保部署的有序性。

**创建顺序：**
```
1. 创建 web-0，等待 Ready
2. 创建 web-1，等待 Ready
3. 创建 web-2，等待 Ready
```

**删除顺序：**
```
1. 删除 web-2，等待完全终止
2. 删除 web-1，等待完全终止
3. 删除 web-0，等待完全终止
```

**配置示例：**
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web
spec:
  serviceName: "web"
  replicas: 3
  podManagementPolicy: OrderedReady  # 有序部署（默认）
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: nginx
        image: nginx:1.21
```

**podManagementPolicy 选项：**

- **OrderedReady**（默认）：有序创建和删除
- **Parallel**：并行创建和删除（Kubernetes 1.7+）

### 7. 什么是持久化存储？

**答案：**

StatefulSet 为每个 Pod 提供独立的持久化存储，Pod 重建后仍能访问相同的数据。

**存储卷模板：**
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web
spec:
  serviceName: "web"
  replicas: 3
  volumeClaimTemplates:
  - metadata:
      name: www
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: "fast-ssd"
      resources:
        requests:
          storage: 10Gi
  template:
    spec:
      containers:
      - name: nginx
        image: nginx:1.21
        volumeMounts:
        - name: www
          mountPath: /usr/share/nginx/html
```

**存储卷命名：**

```
<volumeClaimTemplate-name>-<statefulset-name>-<ordinal>
```

**示例：**
```
www-web-0
www-web-1
www-web-2
```

**存储特性：**

- 每个 Pod 有独立的 PVC
- Pod 删除后 PVC 保留
- Pod 重建后自动绑定到相同的 PVC
- 支持动态和静态存储

---

## 配置详解

### 8. StatefulSet 的基本配置是什么？

**答案：**

**基本配置示例：**
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web
  labels:
    app: web
spec:
  serviceName: "web"              # Headless Service 名称（必需）
  replicas: 3                      # 副本数
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: nginx
        image: nginx:1.21
        ports:
        - containerPort: 80
          name: web
        volumeMounts:
        - name: www
          mountPath: /usr/share/nginx/html
  volumeClaimTemplates:
  - metadata:
      name: www
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 10Gi
```

**必需字段：**

- **serviceName**：Headless Service 名称（必需）
- **selector**：Pod 选择器
- **template**：Pod 模板

### 9. 如何配置 Headless Service？

**答案：**

**Headless Service 配置：**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: web
  labels:
    app: web
spec:
  clusterIP: None                 # Headless Service（必需）
  ports:
  - port: 80
    name: web
  selector:
    app: web
```

**关键配置：**

- **clusterIP: None**：设置为 Headless Service
- **selector**：必须匹配 StatefulSet 的 Pod 标签

**DNS 解析：**

```bash
# 解析到所有 Pod IP
nslookup web.default.svc.cluster.local

# 解析到特定 Pod
nslookup web-0.web.default.svc.cluster.local
```

### 10. 如何配置持久化存储？

**答案：**

**使用 volumeClaimTemplates：**
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql
spec:
  serviceName: mysql
  replicas: 3
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: "fast-ssd"
      resources:
        requests:
          storage: 20Gi
  template:
    spec:
      containers:
      - name: mysql
        image: mysql:8.0
        volumeMounts:
        - name: data
          mountPath: /var/lib/mysql
```

**存储类配置：**
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp3
  fsType: ext4
```

**访问模式：**

- **ReadWriteOnce (RWO)**：单节点读写（StatefulSet 常用）
- **ReadOnlyMany (ROX)**：多节点只读
- **ReadWriteMany (RWX)**：多节点读写

### 11. 如何配置启动和停止钩子？

**答案：**

**使用 Init Containers：**
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql
spec:
  serviceName: mysql
  replicas: 3
  template:
    spec:
      initContainers:
      - name: init-mysql
        image: mysql:8.0
        command:
        - bash
        - "-c"
        - |
          set -ex
          [[ $HOSTNAME =~ -([0-9]+)$ ]] || exit 1
          ordinal=${BASH_REMATCH[1]}
          echo [mysqld] > /mnt/conf.d/server-id.cnf
          echo server-id=$((100 + $ordinal)) >> /mnt/conf.d/server-id.cnf
          cp /mnt/config-map/my.cnf /mnt/conf.d/
        volumeMounts:
        - name: conf
          mountPath: /mnt/conf.d
        - name: config-map
          mountPath: /mnt/config-map
      containers:
      - name: mysql
        image: mysql:8.0
        # ...
```

**使用 Lifecycle Hooks：**
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web
spec:
  template:
    spec:
      containers:
      - name: nginx
        image: nginx:1.21
        lifecycle:
          preStop:
            exec:
              command: ["/bin/sh", "-c", "sleep 15"]
          postStart:
            exec:
              command: ["/bin/sh", "-c", "echo 'Container started'"]
```

---

## 网络标识与 Service

### 12. Headless Service 的作用是什么？

**答案：**

Headless Service 为 StatefulSet 提供稳定的 DNS 解析，允许直接访问每个 Pod。

**关键点：**

- **DNS 名称稳定，IP 不固定**：Pod IP 可能变化，但 DNS 名称始终有效
- **自动更新**：当 Pod IP 变化时，DNS 记录自动更新
- **直接访问**：可以通过 DNS 名称直接访问特定 Pod

**Headless Service 配置：**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: web
spec:
  clusterIP: None              # Headless Service
  ports:
  - port: 80
    name: web
  selector:
    app: web
```

**DNS 解析规则：**

```
# 解析到所有 Pod IP（随机顺序）
web.default.svc.cluster.local
  → 10.244.1.10 (web-0)
  → 10.244.1.11 (web-1)
  → 10.244.1.12 (web-2)

# 解析到特定 Pod IP
web-0.web.default.svc.cluster.local → 10.244.1.10
web-1.web.default.svc.cluster.local → 10.244.1.11
web-2.web.default.svc.cluster.local → 10.244.1.12
```

**使用场景：**

- 主从复制：从节点需要知道主节点地址
- 集群发现：节点需要发现其他节点
- 直接访问：需要访问特定的 Pod

### 13. 如何在应用中使用稳定的网络标识？

**答案：**

**方法 1：使用环境变量**
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web
spec:
  template:
    spec:
      containers:
      - name: nginx
        image: nginx:1.21
        env:
        - name: POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        - name: POD_NAMESPACE
          valueFrom:
            fieldRef:
              fieldPath: metadata.namespace
        - name: SERVICE_NAME
          value: "web"
```

**方法 2：在代码中使用**
```python
import os
import socket

# 获取 Pod 名称
pod_name = os.environ.get('POD_NAME', socket.gethostname())
# pod_name = "web-0"

# 获取 Pod 序号
ordinal = int(pod_name.split('-')[-1])
# ordinal = 0

# 构建其他 Pod 的 DNS 名称
service_name = os.environ.get('SERVICE_NAME', 'web')
namespace = os.environ.get('POD_NAMESPACE', 'default')

for i in range(3):
    if i != ordinal:
        peer_dns = f"{service_name}-{i}.{service_name}.{namespace}.svc.cluster.local"
        # 连接到 peer_dns
```

**方法 3：使用 Downward API**
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web
spec:
  template:
    spec:
      containers:
      - name: nginx
        image: nginx:1.21
        volumeMounts:
        - name: podinfo
          mountPath: /etc/podinfo
      volumes:
      - name: podinfo
        downwardAPI:
          items:
          - path: "labels"
            fieldRef:
              fieldPath: metadata.labels
          - path: "name"
            fieldRef:
              fieldPath: metadata.name
```

---

## 持久化存储

### 14. volumeClaimTemplates 是什么？

**答案：**

volumeClaimTemplates 用于为 StatefulSet 的每个 Pod 自动创建 PersistentVolumeClaim。

**配置示例：**
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql
spec:
  serviceName: mysql
  replicas: 3
  volumeClaimTemplates:
  - metadata:
      name: data
      labels:
        app: mysql
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: "fast-ssd"
      resources:
        requests:
          storage: 20Gi
  template:
    spec:
      containers:
      - name: mysql
        image: mysql:8.0
        volumeMounts:
        - name: data
          mountPath: /var/lib/mysql
```

**生成的 PVC：**

```
data-mysql-0
data-mysql-1
data-mysql-2
```

**特性：**

- 每个 Pod 自动创建独立的 PVC
- Pod 删除后 PVC 保留
- Pod 重建后自动绑定到相同的 PVC
- 支持动态和静态存储

### 15. 如何配置存储类（StorageClass）？

**答案：**

**创建 StorageClass：**
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp3
  fsType: ext4
  encrypted: "true"
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
```

**在 StatefulSet 中使用：**
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql
spec:
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      storageClassName: fast-ssd
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 20Gi
```

**volumeBindingMode：**

- **Immediate**：立即绑定（默认）
- **WaitForFirstConsumer**：等待 Pod 调度后绑定

### 16. 如何扩展存储卷？

**答案：**

**Kubernetes 1.11+ 支持存储卷扩展：**

**1. 启用存储扩展：**
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: kubernetes.io/aws-ebs
allowVolumeExpansion: true      # 启用扩展
```

**2. 编辑 PVC：**
```bash
# 编辑 PVC
kubectl edit pvc data-mysql-0

# 修改 storage 字段
spec:
  resources:
    requests:
      storage: 50Gi              # 从 20Gi 扩展到 50Gi
```

**3. 验证扩展：**
```bash
# 查看 PVC 状态
kubectl get pvc data-mysql-0

# 查看 Pod 中的存储
kubectl exec mysql-0 -- df -h
```

**注意事项：**

- StorageClass 必须支持扩展（allowVolumeExpansion: true）
- 某些存储类不支持扩展
- 扩展可能需要一些时间

---

## 扩缩容

### 17. StatefulSet 如何扩缩容？

**答案：**

**扩容：**
```bash
# 从 3 个扩展到 5 个
kubectl scale statefulset web --replicas=5
```

**扩容过程：**
```
1. 创建 web-3，等待 Ready
2. 创建 web-4，等待 Ready
```

**缩容：**
```bash
# 从 5 个缩容到 3 个
kubectl scale statefulset web --replicas=3
```

**缩容过程：**
```
1. 删除 web-4，等待完全终止
2. 删除 web-3，等待完全终止
```

**配置示例：**
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web
spec:
  replicas: 3
  podManagementPolicy: OrderedReady  # 有序扩缩容
  # podManagementPolicy: Parallel    # 并行扩缩容
```

### 18. 如何实现优雅缩容？

**答案：**

**使用 preStop Hook：**
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql
spec:
  template:
    spec:
      containers:
      - name: mysql
        image: mysql:8.0
        lifecycle:
          preStop:
            exec:
              command:
              - /bin/sh
              - -c
              - |
                # 从集群中移除节点
                mysql -e "SET GLOBAL wsrep_desync=ON;"
                sleep 30
                # 等待同步完成
```

**使用 terminationGracePeriodSeconds：**
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web
spec:
  template:
    spec:
      terminationGracePeriodSeconds: 60  # 优雅终止时间
      containers:
      - name: nginx
        image: nginx:1.21
        lifecycle:
          preStop:
            exec:
              command: ["/bin/sh", "-c", "sleep 15"]
```

**缩容脚本示例：**
```bash
#!/bin/bash
# 优雅缩容脚本

# 1. 标记节点为维护模式
kubectl label pod web-4 maintenance=true

# 2. 等待流量迁移
sleep 30

# 3. 缩容
kubectl scale statefulset web --replicas=3

# 4. 等待 Pod 完全终止
kubectl wait --for=delete pod/web-4 --timeout=60s
```

---

## 更新策略

### 19. StatefulSet 的更新策略有哪些？

**答案：**

**更新策略类型：**

1. **RollingUpdate**（默认）：滚动更新
2. **OnDelete**：手动删除 Pod 触发更新

**RollingUpdate 配置：**
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web
spec:
  updateStrategy:
    type: RollingUpdate
    rollingUpdate:
      partition: 0              # 从索引 0 开始更新
      maxUnavailable: 1        # 最多不可用 Pod 数（Kubernetes 1.7+）
```

**OnDelete 配置：**
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web
spec:
  updateStrategy:
    type: OnDelete
```

**更新过程（RollingUpdate）：**
```
1. 更新 web-2（逆序）
2. 等待 web-2 Ready
3. 更新 web-1
4. 等待 web-1 Ready
5. 更新 web-0
6. 等待 web-0 Ready
```

### 20. 如何使用分区更新（Partitioned Updates）？

**答案：**

**分区更新允许部分 Pod 保持旧版本：**

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web
spec:
  updateStrategy:
    type: RollingUpdate
    rollingUpdate:
      partition: 2              # 只更新索引 >= 2 的 Pod
```

**更新过程：**
```
partition=2 时：
- web-0, web-1 保持旧版本
- web-2 更新到新版本

partition=1 时：
- web-0 保持旧版本
- web-1, web-2 更新到新版本

partition=0 时：
- 所有 Pod 更新到新版本
```

**使用场景：**

- **金丝雀发布**：先更新部分 Pod 测试
- **分阶段更新**：逐步更新所有 Pod
- **回滚准备**：保留部分旧版本 Pod

**操作示例：**
```bash
# 1. 设置 partition=2，只更新 web-2
kubectl patch statefulset web -p '{"spec":{"updateStrategy":{"rollingUpdate":{"partition":2}}}}'

# 2. 更新镜像
kubectl set image statefulset/web nginx=nginx:1.22

# 3. 验证只有 web-2 更新
kubectl get pods -l app=web

# 4. 逐步降低 partition，更新其他 Pod
kubectl patch statefulset web -p '{"spec":{"updateStrategy":{"rollingUpdate":{"partition":1}}}}'
kubectl patch statefulset web -p '{"spec":{"updateStrategy":{"rollingUpdate":{"partition":0}}}}'
```

### 21. 如何回滚 StatefulSet？

**答案：**

**方法 1：使用 kubectl rollout**
```bash
# 查看历史版本
kubectl rollout history statefulset/web

# 回滚到上一个版本
kubectl rollout undo statefulset/web

# 回滚到指定版本
kubectl rollout undo statefulset/web --to-revision=2
```

**方法 2：使用分区更新回滚**
```bash
# 1. 设置 partition，保留旧版本 Pod
kubectl patch statefulset web -p '{"spec":{"updateStrategy":{"rollingUpdate":{"partition":1}}}}'

# 2. 更新镜像到旧版本
kubectl set image statefulset/web nginx=nginx:1.21

# 3. 逐步降低 partition
kubectl patch statefulset web -p '{"spec":{"updateStrategy":{"rollingUpdate":{"partition":0}}}}'
```

**方法 3：直接编辑**
```bash
# 编辑 StatefulSet
kubectl edit statefulset web

# 修改镜像版本
# image: nginx:1.21  # 回滚到旧版本
```

---

## 使用场景

### 22. 数据库集群部署示例

**答案：**

**MySQL 主从复制：**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: mysql
  labels:
    app: mysql
spec:
  ports:
  - port: 3306
    name: mysql
  clusterIP: None
  selector:
    app: mysql
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql
spec:
  serviceName: mysql
  replicas: 3
  selector:
    matchLabels:
      app: mysql
  template:
    metadata:
      labels:
        app: mysql
    spec:
      initContainers:
      - name: init-mysql
        image: mysql:8.0
        command:
        - bash
        - "-c"
        - |
          set -ex
          [[ $HOSTNAME =~ -([0-9]+)$ ]] || exit 1
          ordinal=${BASH_REMATCH[1]}
          if [[ $ordinal -eq 0 ]]; then
            echo [mysqld] > /mnt/conf.d/server-id.cnf
            echo server-id=1 >> /mnt/conf.d/server-id.cnf
            echo binlog-do-db=mydb >> /mnt/conf.d/server-id.cnf
          else
            echo [mysqld] > /mnt/conf.d/server-id.cnf
            echo server-id=$((100 + $ordinal)) >> /mnt/conf.d/server-id.cnf
          fi
          cp /mnt/config-map/my.cnf /mnt/conf.d/
        volumeMounts:
        - name: conf
          mountPath: /mnt/conf.d
        - name: config-map
          mountPath: /mnt/config-map
      containers:
      - name: mysql
        image: mysql:8.0
        env:
        - name: MYSQL_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mysql-secret
              key: password
        ports:
        - name: mysql
          containerPort: 3306
        volumeMounts:
        - name: data
          mountPath: /var/lib/mysql
          subPath: mysql
        - name: conf
          mountPath: /etc/mysql/conf.d
      volumes:
      - name: config-map
        configMap:
          name: mysql-config
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: fast-ssd
      resources:
        requests:
          storage: 20Gi
```

### 23. Kafka 集群部署示例

**答案：**

**Kafka StatefulSet：**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: kafka
  labels:
    app: kafka
spec:
  ports:
  - port: 9092
    name: kafka
  clusterIP: None
  selector:
    app: kafka
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: kafka
spec:
  serviceName: kafka
  replicas: 3
  selector:
    matchLabels:
      app: kafka
  template:
    metadata:
      labels:
        app: kafka
    spec:
      containers:
      - name: kafka
        image: confluentinc/cp-kafka:7.4.0
        ports:
        - containerPort: 9092
          name: kafka
        env:
        - name: KAFKA_BROKER_ID
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        - name: KAFKA_ZOOKEEPER_CONNECT
          value: zookeeper:2181
        - name: KAFKA_ADVERTISED_LISTENERS
          value: PLAINTEXT://$(HOSTNAME).kafka.default.svc.cluster.local:9092
        - name: KAFKA_LISTENERS
          value: PLAINTEXT://0.0.0.0:9092
        - name: KAFKA_LOG_DIRS
          value: /var/lib/kafka/data
        volumeMounts:
        - name: data
          mountPath: /var/lib/kafka/data
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: fast-ssd
      resources:
        requests:
          storage: 100Gi
```

### 24. Elasticsearch 集群部署示例

**答案：**

**Elasticsearch StatefulSet：**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: elasticsearch
  labels:
    app: elasticsearch
spec:
  ports:
  - port: 9200
    name: http
  - port: 9300
    name: transport
  clusterIP: None
  selector:
    app: elasticsearch
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: elasticsearch
spec:
  serviceName: elasticsearch
  replicas: 3
  selector:
    matchLabels:
      app: elasticsearch
  template:
    metadata:
      labels:
        app: elasticsearch
    spec:
      containers:
      - name: elasticsearch
        image: docker.elastic.co/elasticsearch/elasticsearch:8.10.0
        ports:
        - containerPort: 9200
          name: http
        - containerPort: 9300
          name: transport
        env:
        - name: cluster.name
          value: k8s-logs
        - name: node.name
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        - name: discovery.seed_hosts
          value: "elasticsearch-0.elasticsearch,elasticsearch-1.elasticsearch,elasticsearch-2.elasticsearch"
        - name: cluster.initial_master_nodes
          value: "elasticsearch-0,elasticsearch-1,elasticsearch-2"
        - name: ES_JAVA_OPTS
          value: "-Xms2g -Xmx2g"
        volumeMounts:
        - name: data
          mountPath: /usr/share/elasticsearch/data
        resources:
          requests:
            memory: "4Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: fast-ssd
      resources:
        requests:
          storage: 100Gi
```

---

## 最佳实践

### 25. StatefulSet 配置最佳实践

**答案：**

**1. 使用 Headless Service**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: web
spec:
  clusterIP: None  # 必须设置为 None
  selector:
    app: web
```

**2. 配置合适的存储类**
```yaml
volumeClaimTemplates:
- metadata:
    name: data
  spec:
    storageClassName: fast-ssd  # 明确指定存储类
    accessModes: [ "ReadWriteOnce" ]
    resources:
      requests:
        storage: 20Gi
```

**3. 设置资源限制**
```yaml
template:
  spec:
    containers:
    - name: app
      resources:
        requests:
          memory: "512Mi"
          cpu: "500m"
        limits:
          memory: "1Gi"
          cpu: "1000m"
```

**4. 配置健康检查**
```yaml
template:
  spec:
    containers:
    - name: app
      livenessProbe:
        httpGet:
          path: /health
          port: 8080
        initialDelaySeconds: 30
        periodSeconds: 10
      readinessProbe:
        httpGet:
          path: /ready
          port: 8080
        initialDelaySeconds: 5
        periodSeconds: 5
```

**5. 使用 Init Containers 初始化**
```yaml
template:
  spec:
    initContainers:
    - name: init
      image: busybox
      command: ['sh', '-c', 'echo "Initializing..."']
    containers:
    - name: app
      image: myapp:latest
```

### 26. 如何实现高可用？

**答案：**

**1. 多副本部署**
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql
spec:
  replicas: 3  # 至少 3 个副本
```

**2. 反亲和性配置**
```yaml
template:
  spec:
    affinity:
      podAntiAffinity:
        requiredDuringSchedulingIgnoredDuringExecution:
        - labelSelector:
            matchExpressions:
            - key: app
              operator: In
              values:
              - mysql
          topologyKey: kubernetes.io/hostname
```

**3. 跨节点分布**
```yaml
template:
  spec:
    affinity:
      podAntiAffinity:
        preferredDuringSchedulingIgnoredDuringExecution:
        - weight: 100
          podAffinityTerm:
            labelSelector:
              matchExpressions:
              - key: app
                operator: In
                values:
                - mysql
            topologyKey: topology.kubernetes.io/zone
```

**4. 使用 PDB（Pod Disruption Budget）**
```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: mysql-pdb
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: mysql
```

---

## 常见问题与解决方案

### 27. Pod 无法启动怎么办？

**答案：**

**排查步骤：**

1. **查看 Pod 状态：**
```bash
kubectl get pods -l app=web
kubectl describe pod web-0
```

2. **查看 Pod 日志：**
```bash
kubectl logs web-0
kubectl logs web-0 -c init-container
```

3. **检查 PVC 状态：**
```bash
kubectl get pvc
kubectl describe pvc data-web-0
```

4. **检查事件：**
```bash
kubectl get events --sort-by=.metadata.creationTimestamp
```

**常见原因：**

- PVC 无法绑定（存储类问题）
- 镜像拉取失败
- 资源不足
- 配置错误

### 28. Pod 无法访问存储怎么办？

**答案：**

**排查步骤：**

1. **检查 PVC 状态：**
```bash
kubectl get pvc
# 查看是否 Bound
```

2. **检查 PV 状态：**
```bash
kubectl get pv
kubectl describe pv <pv-name>
```

3. **检查存储类：**
```bash
kubectl get storageclass
kubectl describe storageclass fast-ssd
```

4. **检查 Pod 挂载：**
```bash
kubectl exec web-0 -- df -h
kubectl exec web-0 -- mount | grep data
```

**解决方案：**

- 确保 StorageClass 存在且可用
- 检查存储提供者配置
- 验证访问模式（ReadWriteOnce）
- 检查节点资源

### 29. 如何清理 StatefulSet？

**答案：**

**删除 StatefulSet：**
```bash
# 删除 StatefulSet（保留 Pod 和 PVC）
kubectl delete statefulset web

# 删除 StatefulSet 和 Pod（保留 PVC）
kubectl delete statefulset web --cascade=orphan
```

**删除 PVC：**
```bash
# 删除所有 PVC
kubectl delete pvc -l app=web

# 或手动删除
kubectl delete pvc data-web-0 data-web-1 data-web-2
```

**完全清理：**
```bash
# 1. 删除 StatefulSet
kubectl delete statefulset web

# 2. 删除 Pod
kubectl delete pod -l app=web

# 3. 删除 Service
kubectl delete service web

# 4. 删除 PVC
kubectl delete pvc -l app=web
```

---

## 高级特性

### 30. 如何使用 Pod 管理策略（Pod Management Policy）？

**答案：**

**OrderedReady（默认）：**
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web
spec:
  podManagementPolicy: OrderedReady
  replicas: 3
  # 有序创建：web-0 → web-1 → web-2
  # 有序删除：web-2 → web-1 → web-0
```

**Parallel（并行）：**
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web
spec:
  podManagementPolicy: Parallel
  replicas: 3
  # 并行创建：web-0, web-1, web-2 同时创建
  # 并行删除：web-0, web-1, web-2 同时删除
```

**使用场景：**

- **OrderedReady**：需要有序初始化的应用（数据库主从）
- **Parallel**：可以并行启动的应用（Web 服务）

### 31. 如何实现 Pod 间通信？

**答案：**

**使用稳定的 DNS 名称：**
```python
import socket
import os

# 获取当前 Pod 信息
pod_name = os.environ.get('POD_NAME', socket.gethostname())
service_name = os.environ.get('SERVICE_NAME', 'web')
namespace = os.environ.get('POD_NAMESPACE', 'default')

# 构建其他 Pod 的 DNS 名称
def get_peer_dns(ordinal):
    return f"{service_name}-{ordinal}.{service_name}.{namespace}.svc.cluster.local"

# 连接到其他 Pod
for i in range(3):
    peer_dns = get_peer_dns(i)
    # 连接到 peer_dns
```

**使用 Service 发现：**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: web
spec:
  clusterIP: None
  ports:
  - port: 80
  selector:
    app: web
```

**DNS 查询：**
```bash
# 查询所有 Pod IP
nslookup web.default.svc.cluster.local

# 查询特定 Pod IP
nslookup web-0.web.default.svc.cluster.local
```

### 32. StatefulSet 能保证 Pod IP 固定吗？

**答案：**

**不能！StatefulSet 不保证 Pod IP 固定。**

**重要澄清：**

1. **Pod IP 是动态分配的**
   - Kubernetes 中 Pod IP 由 CNI 插件动态分配
   - Pod 重建、节点迁移都会导致 IP 变化
   - 即使是 StatefulSet 也不能保证 IP 不变

2. **StatefulSet 提供的是稳定的 DNS 名称**
   - Pod 名称稳定：`web-0`, `web-1`, `web-2`
   - DNS 名称稳定：`web-0.web.default.svc.cluster.local`
   - IP 可能变化，但 DNS 始终指向正确的 Pod

3. **为什么使用 DNS 而不是 IP？**
   - **IP 会变化**：Pod 重建后 IP 可能改变
   - **DNS 稳定**：DNS 名称始终有效，自动解析到当前 IP
   - **服务发现**：通过 DNS 实现服务发现，不依赖 IP

**示例：**

```bash
# Pod 重建前
web-0 IP: 10.244.1.10
DNS: web-0.web.default.svc.cluster.local → 10.244.1.10

# Pod 重建后
web-0 IP: 10.244.2.15  # IP 改变了！
DNS: web-0.web.default.svc.cluster.local → 10.244.2.15  # DNS 自动更新
```

**如何实现固定 IP？（高级方案）**

如果需要固定 IP，可以使用：

1. **Static IP（某些 CNI 支持）**
   ```yaml
   annotations:
     cni.projectcalico.org/ipAddrs: '["10.244.1.100"]'
   ```

2. **NodePort 或 LoadBalancer**
   - 通过 Service 暴露固定入口
   - 内部仍使用 DNS 名称

3. **External IP**
   - 使用外部 IP 地址
   - 通过 Service 配置

**最佳实践：**

- ✅ **使用 DNS 名称**：`web-0.web.default.svc.cluster.local`
- ❌ **不要依赖 IP 地址**：IP 可能随时变化
- ✅ **使用 Service 发现**：通过 DNS 或 Service 名称访问

### 33. 如何监控 StatefulSet？

**答案：**

**使用 kubectl：**
```bash
# 查看状态
kubectl get statefulset web
kubectl describe statefulset web

# 查看 Pod 状态
kubectl get pods -l app=web

# 查看事件
kubectl get events --field-selector involvedObject.name=web
```

**使用 Prometheus：**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: web-metrics
  labels:
    app: web
spec:
  ports:
  - port: 9090
    name: metrics
  selector:
    app: web
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web
spec:
  template:
    metadata:
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "9090"
        prometheus.io/path: "/metrics"
    spec:
      containers:
      - name: app
        image: myapp:latest
        ports:
        - containerPort: 9090
          name: metrics
```

**自定义监控脚本：**
```bash
#!/bin/bash
# monitor_statefulset.sh

STATEFULSET="web"
NAMESPACE="default"

# 检查副本数
DESIRED=$(kubectl get statefulset $STATEFULSET -n $NAMESPACE -o jsonpath='{.spec.replicas}')
READY=$(kubectl get statefulset $STATEFULSET -n $NAMESPACE -o jsonpath='{.status.readyReplicas}')

if [ "$DESIRED" != "$READY" ]; then
    echo "Warning: $STATEFULSET has $READY/$DESIRED pods ready"
fi

# 检查 Pod 状态
kubectl get pods -l app=$STATEFULSET -n $NAMESPACE
```

---

## 总结

StatefulSet 是 Kubernetes 中管理有状态应用的核心资源，提供了：

1. **稳定的网络标识**：每个 Pod 有唯一且稳定的 DNS 名称（⚠️ 注意：IP 不固定）
2. **有序部署**：按顺序创建和删除 Pod
3. **持久化存储**：每个 Pod 有独立的持久化存储
4. **有序更新**：支持有序的滚动更新和分区更新

**关键理解：**

- ✅ **稳定的 DNS 名称**：`web-0.web.default.svc.cluster.local` 始终有效
- ❌ **不保证 IP 固定**：Pod IP 可能变化，应使用 DNS 名称访问
- ✅ **持久化存储**：Pod 重建后仍能访问相同数据
- ✅ **有序操作**：保证集群初始化和更新的有序性

**适用场景：**

- 数据库集群（MySQL、PostgreSQL、MongoDB）
- 消息队列（Kafka、RabbitMQ）
- 分布式系统（Elasticsearch、ZooKeeper）
- 需要稳定标识和持久化存储的应用

**核心优势：**

- 保证有状态应用的数据持久性
- 提供稳定的网络标识，便于服务发现
- 支持有序操作，适合集群初始化
- 灵活的更新策略，支持金丝雀发布

**学习路径：**

1. 理解 StatefulSet 与 Deployment 的区别
2. 掌握 Headless Service 的配置
3. 学习持久化存储的配置
4. 实践扩缩容和更新操作
5. 掌握最佳实践和故障排查

---

**参考资源：**

- [Kubernetes StatefulSet 官方文档](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/)
- [StatefulSet 基础教程](https://kubernetes.io/docs/tutorials/stateful-application/basic-stateful-set/)
- [运行有状态应用](https://kubernetes.io/docs/tasks/run-application/run-replicated-stateful-application/)

