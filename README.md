# PyFlow

Convenient library to manage data flow in your app by reducing amount of
boilerplate code.

I used Python 3.11. 3.10 must be fine.

There are implementations of same idea for other languages:
- Go: [GoFlow](https://github.com/daiser/goflow)

## What is Flow?

Let's say we need simple app witch parses some strings from STDIN. If string represents
a valid integer number we'll parse it and save into database. Also, we log invalid
strings. Pretty easy, right? But how much boilerplate code we have to write to
make it happen? All that variables, if-statements, error handling. Brrr!

Let's try not so ridgid approach and allow data gently flow through our
application.

```python
import logging
import sys

from flow import Flow


def is_integer(s: str) -> bool:
    try:
        int(s)
        return True
    except ValueError:
        return False


flow = Flow[str]()

valid, invalid = flow. \
    map(lambda s: s.strip()). \
    filter(lambda s: s != ""). \
    segregate(is_integer, True, False)

# invalid strings
invalid.peep(lambda s: logging.error("Invalid integer '%s'", s))

# valid strings
integers = valid. \
    map(int). \
    peep(lambda i: print(f"insert into table(n) values({i});")) \
    .collect()

flow.send(sys.stdin)
print(integers)
```

At first, we created our brand-new Flow. It will gladly accept
strings.

What do we do next? Let's give our strings a little washing
`map(lambda s: s.strip())` and let empty ones go where ever they want to
`filter(lambda s: s != "")`.

Now it's time to parse! But before we begin it would be nice to known which
strings can become Glorious Integers. So we `segregate(is_integer, True, False)`
them into two Flows: `valid` & `invalid`.

Invalid strings have go. Do not hold them. They will find better life
somewhere else. But as they pass, we'll spy on the `invalid`-flow and log every
string we see `invalid.peep(lambda s: logging.error("Invalid integer '%s'", s))`.
Now we have our **logging**.

Ok. Can we parse something already? Yes! `valid.map(int)`! And here they
are! Just look at them! So nice, so shiny and new, so integer!

We worked hard to get them! Well, not so hard, tbh. Because we used Flow.
Anyway, let's `.collect()` them into comfortable `list` and save each one to The
Safe Database along the way: `peep(lambda i: print(f"insert into table(n) values({i});"))`.

Out Flow set up and ready to accept values. Let's `flow.send(sys.stdin)` some into it.

This is it. We and our beloved `integers` lived happily ever after. The end.

## What else can it do?

Actually, not much. But you can be very creative with it.

### next(processor)

This is the core of the Flow. The heart. The blood-fl... oh.

It connects element of Flow to next one (pipe?) and tells how to process 
passing value. If `processor` returns `None` value will not go down the Flow 
any further.

For example, there is no `limit` method in Flow right now. It's easy to
create one.

```python
class Limiter:
    def __init__(self, limit: int):
        self.limit = limit
        self.counter = 0

    def __call__(self, v):
        if self.counter > self.limit:
            return None
        self.counter += 1
        return v

top5 = flow.map(int).next(Limiter(5)).collect()
```
No more than 5 values will pass through this pipe.

You can chain as many processors as you like. At least, until you are
not out of memory. Or your PC.

### filter(filterFunction)

If filter-function returns `True` value passes. Trivial.

### peep(observer)

Allows to "see" each value passing through.

### collect() & collect_to(your_list)

Collect all values reached this point. `collect_to` adds values to the `list`
passed. It's a final stop of a pipe.

### map(mapper)

Do I really need to explain this?

### segregate(classifier, class1, class2, ...)

Splits source Flow into several by the number of classes given.
Than uses `classifier` to... ehm... classify value and send to corresponding
Flow.

### send(values)

Sends a bunch of values into the Flow. You can send values one-by-one by
calling the Flow itself.

Ex., `flow("next_value")`.

### join(flow1, flow2, ...)

Joins given flows into one Mega-Flow. Because, why not?

## Examples

I'll use couple of own functions in examples. There they are:

```python
def is_integer(s: str) -> bool:
    try:
        int(s)
        return True
    except ValueError:
        return False


def save_to_database(n: int):
    # pretend like executing database query. look confident. don't give us away 
    print(f"insert into table(n) values({n});")
```

### 1. Filter and print integers

```python
flow = Flow()
flow.filter(is_integer).peep(print)

flow("1")
flow("2")
flow("Me is genius!")
flow("3")

# Output:
# 1
# 2
# 3
```

### 2. Filter, convert and collect values
```python
flow = Flow()
integers = flow.filter(is_integer).map(int).collect()

flow("1")
flow("2")
flow("three")

print(integers)  # Output: [1, 2]
```

### 3. Collecting into one list from multiple Flows
```python
all_integers = []
evens, odds = Flow(), Flow()
evens.filter(lambda v: v & 1 == 0).collect_to(all_integers)
odds.filter(lambda v: v & 1 == 1).collect_to(all_integers)

evens(0)
evens(2)
evens(5)  # not an even number
odds(1)
odds(3)

print(all_integers)  # Output: [0, 2, 1, 3]
```

### 4. Classification
```python
def classify_height(height: float) -> str:
    if height < 1.6:
        return 'short'
    if height > 1.8:
        return 'tall'
    return 'average'

flow = Flow()
shorts, averages, talls = flow.segregate(classify_height,
                                         'short', 'average', 'tall')
shorts.peep(lambda v: print(v, 'is short'))
averages.peep(lambda v: print(v, 'is average'))
talls.peep(lambda v: print(v, 'is tall'))

flow(1.75)
flow(1.55)
flow(1.85)

# Output:
# 1.75 is average
# 1.55 is short
# 1.85 is tall
```

### 5. Joining
```python
flow = Flow[int]()
squares = flow.map(lambda v: v * v)
cubes = flow.map(lambda v: v * v * v)
numbers = Flow.join(flow, squares, cubes).collect()

flow.send([1, 2, 3])
print(numbers)  # Output: [1, 1, 1, 4, 8, 2, 9, 27, 3]
```
This is tricky. Why numbers not in order: numbers itself, then squares,
then cubes? `squares` & `cubes` are attached to the `flow` and values from 
`flow.send` will be passed to these sub-flows first. So, they'll arrive into
joined flow `numbers` earlier.

# Happy Flowing!
