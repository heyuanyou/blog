---
title: "JavaScript 异步编程复习笔记"
date: 2026-06-15
tags: ["JavaScript", "前端", "笔记"]
summary: "把回调、Promise、async/await 的关系重新捋一遍。"
---

## 回调时代

最早的异步靠回调函数，问题是嵌套多了会形成“回调地狱”，代码难读也难维护。

## Promise

Promise 把异步操作包装成一个对象，可以用 `.then()` 链式调用，把嵌套变成了平铺，也统一了错误处理的方式（`.catch()`）。

## async/await

本质上是 Promise 的语法糖，让异步代码看起来跟同步代码一样，是目前最常用的写法。

```js
async function loadPost(slug) {
  const res = await fetch(`/posts/${slug}.md`);
  return res.text();
}
```

## 常见坑

在循环里滥用 `await` 会让本可以并发的请求变成串行，需要的时候用 `Promise.all` 才对。
