# Java 开发规则

> 文件：`10-java.md`
>
> 定位：定义 AI 在生成、修改、重构和审查 Java 代码时必须遵循的通用 Java 工程规则。
>
> 本文件是 Java 通用规则，不包含 Windchill 平台专用规则。

---

## 1. 适用范围

本规则适用于项目中的所有 Java 源代码，包括：

- 新增 Java 类；
- 修改现有 Java 类；
- 重构已有实现；
- 修复缺陷；
- 编写工具类、服务类、DTO、领域对象等；
- Review Java 代码；
- AI 自动生成 Java 实现。

本规则主要约束：

- Java 语言使用；
- 类型安全；
- API 设计；
- 对象设计；
- 集合使用；
- 空值处理；
- 可变状态；
- 资源管理；
- 并发安全；
- Lambda / Stream 使用；
- 代码可维护性；
- Java 版本兼容性。

以下内容不由本文件定义：

- Windchill API 的选择与使用；
- Windchill 持久化机制；
- Windchill Transaction；
- Windchill JCA / MVC；
- 安全策略；
- 日志策略；
- 异常体系设计；
- 配置管理；
- 测试策略。

上述内容应遵循对应的专项规则文件。

---

## 2. 规则优先级

### MUST

当本规则与更具体的平台规则、框架规则或项目规则发生冲突时，必须遵循更具体的规则。

规则优先级原则：

```text
项目明确需求
    >
平台 / 框架专用规则
    >
Java 通用规则
    >
代码风格与格式规则
```

例如：

```text
Windchill API Rule
    >
Java Rule
```

不得为了遵循所谓“现代 Java 最佳实践”而破坏平台兼容性。

---

## 3. Java 版本与兼容性

### 3.1 不得假设最新 Java 版本

#### MUST

生成代码前必须以项目实际配置的 JDK / Java Language Level 为准。

不得因为当前 JDK 存在某种新语法，就直接在项目代码中使用。

例如不得未经确认直接引入：

```java
record
sealed
var
switch expression
text block
pattern matching
virtual thread
```

### 3.2 不得主动升级 Java Language Level

#### MUST NOT

除非任务明确要求，否则不得修改：

```text
sourceCompatibility
targetCompatibility
maven.compiler.source
maven.compiler.target
maven.compiler.release
```

或其他 Java 编译版本设置。

### 3.3 优先兼容现有代码库

#### SHOULD

如果一种实现写法较新，但对项目 Java 版本存在要求，而另一种实现稍传统但完全兼容现有运行环境，则默认选择兼容现有运行环境的方案。

---

## 4. AI 修改代码的基本原则

### 4.1 最小必要修改

#### MUST

只修改完成当前任务所必需的代码。

不得在实现一个需求时顺便：

- 大规模重命名；
- 改变无关代码格式；
- 替换已有框架；
- 修改无关 API；
- 重新组织整个 package；
- 重构没有问题的代码。

### 4.2 尊重已有代码风格

#### MUST

修改已有代码时，应优先保持当前模块已经形成的：

- 命名方式；
- API 风格；
- 对象创建方式；
- 返回值约定；
- Collection 使用习惯；
- 注解使用方式；
- 工厂方法模式；
- Builder 模式；
- Utility 模式。

除非现有实现存在明确问题，否则不得仅因为另一种写法“更现代”而替换。

### 4.3 不得制造无必要抽象

#### MUST NOT

不得为了表现“架构设计”而创建无实际价值的：

```text
Manager
Helper
Util
Factory
Builder
Adapter
Wrapper
Facade
Strategy
Provider
```

一个抽象必须解决明确问题，例如：

- 解耦；
- 可替换实现；
- 生命周期管理；
- 复用；
- API 隔离；
- 测试边界。

---

## 5. 类型安全

### 5.1 禁止 Raw Type

#### MUST NOT

不得使用原始集合类型。

错误：

```java
List values = new ArrayList();
Map data = new HashMap();
```

正确：

```java
List<String> values = new ArrayList<>();
Map<String, Object> data = new HashMap<>();
```

### 5.2 避免不安全类型转换

#### SHOULD

尽量避免：

```java
(ObjectType) value
```

在无法避免类型转换时，应确保类型来源明确。

必要时先进行类型判断：

```java
if (value instanceof String) {
    String text = (String) value;
}
```

不得通过异常捕获代替类型判断。

### 5.3 谨慎使用 SuppressWarnings

#### MUST

不得使用大范围：

```java
@SuppressWarnings("all")
```

如果确实需要：

```java
@SuppressWarnings("unchecked")
```

必须限制在最小作用域。

不得通过 `SuppressWarnings` 掩盖真实设计问题。

### 5.4 优先使用具体泛型

#### SHOULD

如果类型可以明确表达：

```java
List<WTPart>
```

则不要退化为：

```java
List<Object>
```

泛型应尽可能表达真实的数据语义。

---

## 6. Null 处理

### 6.1 Null 语义必须明确

#### MUST

方法是否允许 `null` 应由 API 语义决定，而不是随意决定。

不得形成调用者无法判断 `null` 含义的模糊接口。

### 6.2 Collection 不返回 null

#### SHOULD

对于 Collection 返回值，优先返回空集合。

推荐：

```java
return Collections.emptyList();
```

而不是：

```java
return null;
```

同样适用于 `List`、`Set`、`Map`、`Collection`。

除非既有 API 明确定义 `null` 有特殊语义。

### 6.3 不得机械使用 Optional

#### MUST NOT

不得把所有可能为空的值都改成：

```java
Optional<T>
```

`Optional` 主要用于表达“返回值可能合法地不存在”。

通常不建议把 `Optional` 用作：

- 字段类型；
- 方法参数；
- DTO 属性；
- 持久化属性。

如果项目或平台 API 已定义其他 null 语义，应遵循平台 API。

### 6.4 API 边界进行必要校验

#### SHOULD

对于公开 API 或业务边界中的必填参数，应尽早校验。

例如：

```java
Objects.requireNonNull(part, "part must not be null");
```

但不得为了“防御性编程”在内部每一层重复进行相同 null 检查。

---

## 7. 对象设计与可变状态

### 7.1 最小化可变状态

#### SHOULD

如果一个对象的状态在创建后无需变化，应优先保持不可变。

例如优先：

```java
private final String number;
```

而不是：

```java
private String number;
```

但不得因为追求不可变而破坏框架要求。

### 7.2 谨慎使用 static 可变状态

#### MUST NOT

不得无必要创建：

```java
private static Map<String, Object> cache = new HashMap<>();
```

如果确实需要共享状态，必须明确考虑：

- 生命周期；
- 并发；
- 内存释放；
- 初始化；
- 集群环境；
- 缓存失效。

### 7.3 不得暴露内部可变对象

#### SHOULD

不得无意暴露内部 Collection。

如果调用者不应修改内部数据，应使用适当方式保护内部状态，例如：

```java
return Collections.unmodifiableList(values);
```

或者返回防御性副本。

但避免无意义复制大型集合。

### 7.4 不要滥用 final

#### SHOULD

`final` 应主要用于表达“此引用在当前作用域内不应重新赋值”。

不要求机械地给所有局部变量添加 `final`。

---

## 8. 方法设计

### 8.1 方法只负责一个清晰职责

#### SHOULD

一个方法应该可以用一句明确的话描述其职责。

如果一个方法同时完成多个不相关步骤，应考虑拆分。

### 8.2 避免过长方法

#### SHOULD

当一个方法同时包含：

```text
参数解析
权限判断
查询
数据转换
业务判断
持久化
响应组装
```

应考虑按职责拆分。

拆分必须基于职责，而不是为了机械降低代码行数。

### 8.3 避免过深嵌套

#### SHOULD

优先使用 Guard Clause 降低嵌套复杂度。

推荐：

```java
if (!condition) {
    return;
}

doSomething();
```

### 8.4 参数数量应可理解

#### SHOULD

当方法包含大量同类型参数时，应检查是否适合使用：

- 参数对象；
- Value Object；
- Builder；
- Context Object。

但不得为了减少少量参数而无意义创建 DTO。

### 8.5 Boolean 参数应语义明确

#### SHOULD

避免：

```java
execute(true, false);
```

如果 boolean 参数较多，应考虑枚举、参数对象或更明确的方法名称。

---

## 9. Collection 使用

### 9.1 面向接口编程

#### SHOULD

声明变量时通常优先使用接口：

```java
List<String> values = new ArrayList<>();
Map<String, Object> data = new HashMap<>();
```

而不是具体实现类型。

### 9.2 根据语义选择 Collection

#### MUST

根据实际需求选择：

```text
List
Set
Map
Queue
Deque
ConcurrentMap
```

需要唯一性时优先考虑 `Set`，不要默认使用 `List + contains()`。

### 9.3 不得依赖未定义的顺序

#### MUST NOT

如果业务逻辑依赖顺序，则必须选择具有明确顺序语义的数据结构。

不得依赖 `HashMap`、`HashSet` 的遍历顺序。

### 9.4 修改 Collection 时遵循其迭代语义

#### MUST

不得在普通增强 `for` 循环中随意修改正在遍历的集合。

应使用：

- `Iterator`；
- `removeIf`；
- 新集合；
- 其他符合 Collection API 的方法。

---

## 10. 字符串、常量与 Magic Value

### 10.1 避免 Magic Value

#### SHOULD

具有明确业务含义的值不应散落在代码中。

例如：

```java
if (status == 5)
```

如果其语义稳定，应定义为常量、枚举或使用平台已有定义。

### 10.2 优先使用已有平台常量

#### MUST

如果 Java SDK、项目或平台已经定义常量，则不得重复硬编码。

### 10.3 不得滥用 String 表达领域概念

#### SHOULD

当一个字段只有有限合法值时，应考虑使用 `enum` 或平台提供的类型，而不是任意 `String`。

前提是不会与现有框架、持久化或 API 设计冲突。

---

## 11. Enum

### 11.1 有限状态优先考虑 Enum

#### SHOULD

有限且稳定的状态集合，通常优先考虑枚举。

### 11.2 不依赖 ordinal

#### MUST NOT

不得把：

```java
enum.ordinal()
```

作为：

- 数据库存储值；
- 外部系统接口值；
- 持久化协议；
- 业务编号。

应使用明确稳定的业务值。

---

## 12. 资源管理

### 12.1 明确资源所有权

#### MUST

关闭资源前必须明确当前代码是否拥有该资源。

不得关闭由框架、容器或调用方管理生命周期的资源。

### 12.2 自己创建的 AutoCloseable 应及时关闭

#### MUST

对于当前代码负责创建和拥有的资源，应优先使用：

```java
try (InputStream input = ...) {
    ...
}
```

适用对象包括但不限于：

```text
InputStream
OutputStream
Reader
Writer
JDBC Connection
Statement
ResultSet
```

具体生命周期仍应遵循框架要求。

---

## 13. 并发

### 13.1 不假设代码只运行在一个线程

#### MUST

服务器端代码默认应认为同一个类或服务可能被多个线程同时访问。

尤其应谨慎处理：

```text
static 字段
Singleton
Cache
共享 Collection
共享 Formatter
```

### 13.2 优先使用 java.util.concurrent

#### SHOULD

并发场景优先使用 Java 提供的成熟抽象：

```text
ConcurrentHashMap
AtomicInteger
ExecutorService
BlockingQueue
CompletableFuture
```

而不是自行构造复杂的 `wait()/notify()` 逻辑。

### 13.3 不要随意 synchronized

#### MUST NOT

不得把 `synchronized` 作为解决并发问题的默认方案。

使用前必须理解：

- 锁对象；
- 锁粒度；
- 阻塞范围；
- 是否可能死锁；
- 是否影响吞吐量。

### 13.4 不在公开对象上加锁

#### MUST NOT

避免：

```java
synchronized (somePublicObject) {
}
```

或：

```java
synchronized ("LOCK") {
}
```

锁对象应由实现内部控制。

### 13.5 谨慎使用 parallelStream

#### MUST NOT

不得因为 Stream 支持并行就主动并行化。

尤其在应用服务器、数据库操作、Windchill MethodServer、IO 操作、事务上下文中，不得未经分析使用 `parallelStream()`。

---

## 14. Lambda 与 Stream

### 14.1 Stream 不是强制风格

#### MUST NOT

不得把所有循环机械改写为 Stream。

### 14.2 简单转换适合 Stream

#### SHOULD

如果 Stream 能明显提高表达能力，可用于简单转换、过滤、聚合。

### 14.3 避免具有副作用的复杂 Stream

#### SHOULD

不要在复杂 Stream 中同时：

- 修改对象；
- 写数据库；
- 修改外部状态；
- 修改共享集合。

这种场景通常普通循环更清晰。

### 14.4 Lambda 应保持短小

#### SHOULD

如果 Lambda 内部包含复杂业务逻辑，应提取为具名方法。

---

## 15. 日期与时间

### 15.1 新代码优先考虑 java.time

#### SHOULD

如果项目 Java 版本和平台 API 允许，新代码优先考虑：

```text
Instant
LocalDate
LocalDateTime
ZonedDateTime
Duration
```

### 15.2 平台 API 优先

#### MUST

如果平台 API 明确要求 `Timestamp`、`Date` 或其他时间类型，则遵循平台 API。

不得为了使用 `java.time` 而无意义地来回转换。

### 15.3 注意时区语义

#### MUST

涉及数据库时间、服务器时间、用户输入时间、跨系统接口时间、UTC 时间时不得忽略时区。

不得默认认为服务器时区等于用户时区。

---

## 16. equals、hashCode 与 compareTo

### 16.1 equals 与 hashCode 必须一致

#### MUST

如果覆盖 `equals()`，则必须同时检查并正确实现 `hashCode()`。

### 16.2 不随意覆盖框架对象的 equals/hashCode

#### MUST NOT

对于 ORM 对象、持久化对象、Windchill 对象、Framework-managed Object，不得在不了解平台语义的情况下主动覆盖 `equals()` / `hashCode()`。

平台规则优先。

### 16.3 compareTo 与 equals 的语义要明确

#### SHOULD

如果对象实现 `Comparable`，必须明确 `compareTo() == 0` 是否与 `equals() == true` 保持一致。

---

## 17. 继承与组合

### 17.1 优先组合而非无意义继承

#### SHOULD

只有存在明确 `is-a` 关系时才使用继承。

不要仅为了复用几个方法而创建继承关系。

### 17.2 不继承仅为访问 protected

#### MUST NOT

不得为了访问某个类的 `protected` 方法而创建没有领域意义的子类。

### 17.3 平台扩展点例外

#### MUST

如果平台明确要求通过 `extends` / `implements` 实现扩展，则必须遵循平台提供的扩展模型。

---

## 18. Utility 类

### 18.1 Utility 类必须真正无状态

#### SHOULD

典型 Utility：

```java
public final class StringUtils {

    private StringUtils() {
    }

    public static ...
}
```

Utility 类不应保存请求级或用户级状态。

### 18.2 不创建万能 Utils

#### MUST NOT

禁止创建类似：

```text
CommonUtils
AppUtils
GeneralUtils
MiscUtils
```

然后不断往里面堆无关方法。

Utility 应围绕明确职责。

---

## 19. API 与依赖

### 19.1 优先使用项目已有依赖

#### MUST

实现功能前应先检查：

- JDK 是否已有 API；
- 项目是否已有工具类；
- 当前依赖是否已经提供功能；
- 平台是否提供官方 API。

不得因为少量代码就随意增加第三方依赖。

### 19.2 不得无授权升级依赖

#### MUST NOT

除非任务明确要求，不得修改：

```text
Maven dependency version
Gradle dependency version
Java SDK version
Framework version
```

### 19.3 避免使用 Internal API

#### MUST NOT

不得使用：

```text
sun.*
com.sun.*
jdk.internal.*
```

等 JDK 内部 API。

平台明确要求的特殊情况除外。

### 19.4 谨慎使用 Reflection

#### SHOULD

不得为了规避正常 API 而使用：

```java
setAccessible(true)
```

Reflection 仅适用于框架扩展、元数据处理、动态加载等确有必要的场景。

---

## 20. 性能

### 20.1 不进行无依据的微优化

#### MUST NOT

不得因为“可能更快”而降低代码可读性。

优化应优先针对：

```text
数据库访问
网络访问
磁盘 IO
大对象
大集合
重复计算
算法复杂度
```

### 20.2 注意循环中的昂贵操作

#### SHOULD

看到以下结构时必须检查：

```java
for (...) {
    queryDatabase();
}
```

或：

```java
for (...) {
    callRemoteService();
}
```

应考虑是否存在 N+1 查询、重复 RPC、重复文件 IO。

### 20.3 避免无意义创建对象

#### SHOULD

在大循环、批处理或高频调用路径中，应避免明显不必要的临时对象创建。

---

## 21. 命名

### 21.1 名称应表达业务语义

#### MUST

避免：

```java
String str;
Object obj;
List list;
Map map;
int temp;
Object data;
```

如果存在明确语义，应使用：

```java
String partNumber;
WTPart part;
List<WTPart> parts;
Map<String, WTPart> partsByNumber;
```

### 21.2 避免无意义缩写

#### SHOULD

除非是项目或行业已经广泛接受的术语，否则不要创造难懂缩写。

可以接受：

```text
DTO
URL
HTTP
XML
JSON
OID
BOM
```

### 21.3 Boolean 名称表达判断含义

#### SHOULD

优先：

```java
isEnabled
hasPermission
canModify
shouldRefresh
```

而不是：

```java
flag
status
value
check
```

---

## 22. 注释与 Javadoc

### 22.1 注释解释 Why，不重复 What

#### SHOULD

错误：

```java
// Increase count by 1
count++;
```

注释应解释设计原因、约束、平台行为或特殊业务语义。

### 22.2 不保留失效注释

#### MUST

修改实现后，如果原注释已经不再正确，应同步更新或删除。

### 22.3 不使用注释保留废弃代码

#### MUST NOT

不得通过注释保留旧实现。

Git 已经负责历史版本管理。

### 22.4 Public API 应有必要说明

#### SHOULD

对于公共 API、复杂业务方法、非显而易见的扩展点，应考虑使用 Javadoc 描述：

- 方法职责；
- 参数语义；
- 返回值语义；
- 重要约束；
- 副作用。

不要为显而易见的 getter/setter 机械生成 Javadoc。

---

## 23. 代码格式与静态检查

本文件不详细定义：

```text
缩进
空格
换行
import 顺序
大括号风格
最大行宽
文件结尾换行
```

这些规则应优先由以下工具统一处理：

```text
.editorconfig
IntelliJ Code Style
Checkstyle
Spotless
PMD
Sonar
```

AI 不应为了满足自己的代码风格偏好而重新格式化整个文件。

---

## 24. 禁止事项汇总

除非存在明确的平台、框架或项目要求，否则禁止：

- 使用 Raw Type；
- 大范围 `@SuppressWarnings`；
- 使用 `@SuppressWarnings("all")`；
- Collection 返回 `null`；
- 无理由增加第三方依赖；
- 无理由升级 Java 版本；
- 使用 JDK Internal API；
- 无依据使用 Reflection；
- 无依据使用 `parallelStream()`；
- 创建共享可变 static Collection；
- 使用 `enum.ordinal()` 作为持久化值；
- 使用 Magic Number 表达业务状态；
- 创建无实际价值的抽象层；
- 创建万能 `CommonUtils`；
- 顺手重构无关代码；
- 为追求“现代 Java”破坏平台兼容性；
- 修改 Framework-generated Code，除非平台明确要求；
- 假设服务器端代码只有一个线程访问。

---

## 25. AI 生成代码前检查

生成或修改 Java 代码之前，应检查：

1. 当前项目使用哪个 Java/JDK 版本？
2. 当前模块是否已有相似实现？
3. 是否可以复用已有 API？
4. 是否存在平台专用规则？
5. 是否引入了新的依赖？
6. 是否引入共享可变状态？
7. 是否存在潜在 null 语义问题？
8. 是否正确选择 Collection？
9. 是否存在不必要类型转换？
10. 是否可能产生并发问题？
11. 是否可能产生资源泄漏？
12. 是否修改了任务范围之外的代码？

---

## 26. AI 生成代码后检查

完成 Java 代码后，应至少检查：

- 代码是否兼容当前 Java 版本；
- 是否存在 Raw Type；
- 是否存在 unchecked warning；
- Collection 是否可能返回 null；
- 是否产生不必要的 Optional；
- 是否引入 mutable static state；
- 资源是否正确管理；
- Stream 是否过于复杂；
- Lambda 是否包含过多业务逻辑；
- 方法是否职责过多；
- 是否存在明显 N+1 调用；
- 是否重复实现已有 API；
- 是否修改了不相关代码；
- 是否违反更高优先级的平台规则。

---

## 27. 规则设计原则

本文件遵循以下原则：

> Java Rule 应主要约束“需要工程判断才能正确处理的问题”。

能够稳定交由以下工具完成的事情：

```text
Compiler
Formatter
Checkstyle
Spotless
PMD
Sonar
```

不应重复写成大量 AI Rule。

Java Rule 应保持：

```text
高信号
低歧义
低重复
可执行
可审查
平台兼容优先
```
