import typing

TValue = typing.TypeVar("TValue")
TMappedValue = typing.TypeVar("TMappedValue")
TClass = typing.TypeVar("TClass")

TProcessor = typing.Callable[[TValue], TValue | None]
"""This is how you processing values."""
TFilter = typing.Callable[[TValue], bool]
"""This is how you filter values."""
TObserver = typing.Callable[[TValue], None]
"""This is how you peeping values."""
TMapper = typing.Callable[[TValue], TMappedValue]
"""This is how you map values."""
TClassificator = typing.Callable[[TValue], TClass | typing.Iterable[TClass]]
"""This is how you classifying values."""
TSelector = typing.Callable[[TValue], typing.Iterable[TMappedValue]]
"""This is how you select values."""


class Flow(typing.Generic[TValue]):
    def __init__(self, processor: TProcessor = None):
        self._children: list[Flow[TValue]] = list()
        self._processor: TProcessor = \
            processor if processor is not None else lambda v: v  # pass value
        self._collection: list[TValue] = list()

    def next(self, processor: TProcessor) -> 'Flow[TValue]':
        """Adds any processor you like. Flow stops if None returned."""
        flow = Flow(processor)
        self._children.append(flow)
        return flow

    def filter(self, filter_callback: TFilter) -> 'Flow[TValue]':
        """Trues are passing. Pretty trivial."""
        return self.next(lambda v: v if filter_callback(v) else None)

    def peep(self, observer: TObserver) -> 'Flow[TValue]':
        """You can see any value passing through. And do anything with it."""
        return self.next(lambda v: _observe(v, observer))

    def collect(self) -> list[TValue]:
        self.next(lambda v: self._collection.append(v))
        return self._collection

    def collect_to(self, your_list: list[TValue]):
        self.next(lambda v: your_list.append(v))

    def map(self, mapper: TMapper) -> 'Flow[TMappedValue]':
        """Maps each value to new value and goes on."""
        return self.next(lambda v: mapper(v))

    def segregate(self,
                  classificator: TClassificator,
                  *classes: TClass,
                  unclassified: bool = False) -> tuple['Flow[TValue]', ...]:
        """Source flow splits into several flows by the number of classes
         passed. For each value `classificator` tells its class and values goes
         to the corresponding flow. Useful indeed."""
        classificator = _Classificator(classificator,
                                       list(classes),
                                       unclassified)
        self.next(classificator)
        return classificator.flows

    def select(self, selector: TSelector) -> 'Flow[TMappedValue]':
        """For each input value runs selector and sends its output
         to new a Flow."""
        selection_flow = Flow[TMappedValue]()
        self.next(lambda value: selection_flow.send(selector(value)))
        return selection_flow

    def count(self, setter: typing.Callable[[int], None]) -> 'Flow[TValue]':
        """Counts values passes and updates external variable
        via provided `setter` callback."""
        counter = 0

        def count(value: TValue) -> TValue:
            nonlocal counter
            counter += 1
            setter(counter)
            return value

        return self.next(count)

    def __call__(self, v: TValue):
        result = self._processor(v)
        if result is not None:
            for child in self._children:
                child(result)

    # service methods
    def send(self, values: typing.Iterable[TValue]):
        """Sends the bunch of values through the flow. Bon voyage!"""
        for value in values:
            self(value)

    @staticmethod
    def join(*flows: 'Flow[TValue]') -> 'Flow[TValue]':
        """Joins several flows into new mega-flow!"""
        joined_flow = Flow[TValue]()
        for flow in flows:
            flow._children.append(joined_flow)
        return joined_flow


class _Classificator(typing.Generic[TValue, TClass]):
    def __init__(self,
                 classificator: TClassificator,
                 classes: list[TClass],
                 unclassified_flow: bool):
        if not classes:
            raise ValueError("empty classes")
        if len(classes) != len(set(classes)):
            raise ValueError("non unique classes")

        self._classify = classificator
        self._flows_in_order: list[Flow[TValue]] = list()
        self._directions: dict[TClass, Flow[TValue]] = dict()

        for class_ in classes:
            class_flow = Flow[TValue]()
            self._flows_in_order.append(class_flow)
            self._directions[class_] = class_flow

        self._unclassified: Flow[TValue] | None = None
        if unclassified_flow:
            self._unclassified = Flow[TValue]()
            self._flows_in_order.append(self._unclassified)

    @property
    def flows(self) -> tuple[Flow[TValue], ...]:
        return tuple(self._flows_in_order)

    def _get_directions(self, classes: TClass | typing.Iterable[TClass]) \
            -> typing.Generator[Flow[TValue] | None, None, None]:
        try:
            for class_ in classes:
                if class_ in self._directions:
                    yield self._directions[class_]
        except TypeError:
            yield from self._get_directions([classes])

    def __call__(self, v: TValue) -> TValue | None:
        directions = list(self._get_directions(self._classify(v)))
        if directions:
            for flow in directions:
                flow(v)
        elif self._unclassified is not None:
            self._unclassified(v)
        return None  # stop source flow


def _observe(v: TValue, observer: TObserver) -> TValue:
    observer(v)
    return v
