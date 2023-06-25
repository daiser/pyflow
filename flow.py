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
TClassificator = typing.Callable[[TValue], TClass]
"""This is how you classifying values."""


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
        return self.next(lambda v: _snitch_and_pass(v, observer))

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
                  *classes: TClass) -> tuple['Flow[TValue]', ...]:
        """Source flow splits into several flows by the number of classes
         passed. For each value `classificator` tells its class and values goes
         to the corresponding flow. Useful indeed."""
        classificator = _Classificator(classificator, list(classes))
        self.next(classificator)
        return classificator.flows

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
    def __init__(self, classify: TClassificator, classes: list[TClass]):
        if not classes:
            raise ValueError("empty classes")
        if len(classes) != len(set(classes)):
            raise ValueError("non unique classes")

        self._classify = classify
        self._flows_in_order: list[Flow[TValue]] = list()
        self._directions: dict[TClass, Flow[TValue]] = dict()

        for class_ in classes:
            class_flow = Flow[TValue]()
            self._flows_in_order.append(class_flow)
            self._directions[class_] = class_flow

        self._unclassified = Flow[TValue]()
        self._flows_in_order.append(self._unclassified)

    @property
    def flows(self) -> tuple[Flow[TValue], ...]:
        return tuple(self._flows_in_order)

    def __call__(self, v: TValue) -> TValue | None:
        class_ = self._classify(v)
        self._directions.get(class_, self._unclassified)(v)
        return None  # stop source flow


def _snitch_and_pass(v: TValue, snitch: TObserver) -> TValue:
    snitch(v)
    return v
