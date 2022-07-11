JoPlan - Arrange Jobs as Plan
=============================

## Installation

```shell
$ pip install joplan
```

## Usage

```python
from joplan import do, every, Plan

Plan([
    do('pkg.mod.func1').every('5s'),
    do('pkg.mod.func2').every('3m'),
]).run()
```
