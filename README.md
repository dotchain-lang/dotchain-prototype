# Dotchain
Dotchain 是一種函數式編程語言. 文件後綴`.dc`

# 語法
```
// 註解

// 變量宣告
let hello = 123

// 函數宣告
let add = (left, right) => {
  // 返回值
  return left + right
}

// TODO： 函數呼叫
add(1,2)
add(3, add(1,2))
// 以 . 呼叫函數，將以 . 前的值作為第一個參數
// hello.add(2) 等價於 add(hello, 2)
```
## Keywords
```
let while if else true false
```

```bash
python -m unittest
```