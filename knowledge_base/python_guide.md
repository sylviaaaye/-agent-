# Python 编程指南

## 基础知识

Python是一种高级编程语言，以其简洁的语法和丰富的生态系统而闻名。

### 数据类型
- 数字（int, float, complex）
- 字符串（str）
- 列表（list）
- 元组（tuple）
- 字典（dict）
- 集合（set）

### 控制流
```python
# if语句
if condition:
    do_something()
elif other_condition:
    do_other_thing()
else:
    do_default()

# for循环
for item in items:
    process(item)

# while循环
while condition:
    do_something()
```

## 高级特性

### 列表推导式
```python
squares = [x**2 for x in range(10)]
```

### 装饰器
```python
def my_decorator(func):
    def wrapper():
        print("Something is happening before the function is called.")
        func()
        print("Something is happening after the function is called.")
    return wrapper

@my_decorator
def say_hello():
    print("Hello!")
```

### 生成器
```python
def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b
```

## 最佳实践

1. 使用有意义的变量名
2. 编写文档字符串
3. 遵循PEP 8风格指南
4. 适当使用异常处理
5. 编写单元测试

## 常见库

- requests: HTTP请求
- pandas: 数据分析
- numpy: 科学计算
- flask/django: Web开发
- tensorflow/pytorch: 机器学习 