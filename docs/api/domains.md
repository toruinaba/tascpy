# Domains モジュール

`tascpy.domains` の API リファレンスです。ドメインごとに、コレクション（設定）、操作（`coll.ops`）、描画（`coll.plot`）があります。変換は `col.ops.as_domain(as_load_displacement, ...)` のように、各ドメインの変換関数を渡して行います。

## 荷重-変位

### LoadDisplacementCollection
::: tascpy.domains.load_displacement.collection

### LoadDisplacementOps
::: tascpy.domains.load_displacement.ops

### LoadDisplacementPlotter
::: tascpy.domains.load_displacement.plotter

### 描画関数
::: tascpy.domains.load_displacement.draw

## 座標

### CoordinateCollection
::: tascpy.domains.coordinate.collection

### CoordinateOps
::: tascpy.domains.coordinate.ops

## ひずみ

### StrainCollection
::: tascpy.domains.strain.collection

### StrainOps
::: tascpy.domains.strain.ops

### StrainPlotter
::: tascpy.domains.strain.plotter

### 描画関数
::: tascpy.domains.strain.draw
