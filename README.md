# 項目介紹
這個倉庫用於語法驗證和可行性分析，使用python構建簡易的直譯器和運行時。
# Dotchain
Dotchain 是一種函數式編程語言. 文件後綴`.dc`，命名為dot chain是因為我希望這個語言風格主要以`.`鏈式調用為主。啓發自`Elixir`的管道符號`|>`，如果直接使用`.`作為管道符是不是更方便。而取得構結中的屬性則使用`->`符號。
# 運行時
Dotchain runtime將會是一個特別的運行時，一個雲原生的運行時，它將原生支持FaaS。它會是一個厚重的運行時，可以直接作為容器被cgroups和k8s運行。甚至能作為虛擬機直接啓動於QEMU中。我一相情願的想法是運行時將越來越厚重，直接在運行時上實現container cri，可直接被k8s等技術管理。
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
```
## Keywords
```
let while if else true false
```

```bash
python main.py
```
