JoPlan - Arrange Jobs as Plan
=============================

## Installation

```shell
$ pip install joplan
```

## Usage

### Demo 1

```python
import logging

from joplan import take, do, every

logging.basicConfig(level=logging.INFO)

def f1():
    print('Making F1')

def f2():
    print('Making F2')

take(
    every('2s').do(f1),
    every('3s').do(f2),
).run()
```

### Demo 2

```python
from joplan import take, do, every

take(
    do('pkg.mod.func1').every('5s'),
    do('pkg.mod.func2').every('3m'),
).run()
```
