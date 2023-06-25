import pytest

from flow import Flow, _Classificator as Classificator


def _value_is_class(value: str) -> str: return value


class TestFlow:
    def test_filter(self):
        f = Flow[int]()
        evens = f.filter(lambda n: n % 2 == 0).collect()
        f.send([1, 2, 3, 4])

        assert evens == [2, 4]

    def test_collect(self):
        f = Flow[str]()
        strings = f.collect()
        f("a")
        f("b")
        f("c")
        assert strings == ["a", "b", "c"]

    def test_collect_to(self):
        my_list = []
        f = Flow[int]()
        f.collect_to(my_list)
        f(1)
        f.send([2, 3])
        assert my_list == [1, 2, 3]

    def test_peep(self):
        peeped = []
        f = Flow[str]()
        f.peep(lambda s: peeped.append(s))
        f.send(["a", "b", "c"])
        assert peeped == ["a", "b", "c"]


class TestClassificator:
    def test_invalid_ctor(self):
        with pytest.raises(ValueError):
            Classificator(lambda v: v, [], False)  # no classes
        with pytest.raises(ValueError):
            Classificator(lambda v: v,
                          ["a", "b", "a", "c"],
                          False)  # duplicate classes

    def test_unclassified_flow(self):
        c = Classificator(_value_is_class, ["a", "b"], True)
        flows = c.flows
        assert len(flows) == 3, "invalid number of flows created"

        flow_a, flow_b, flow_uc = flows
        a_list = flow_a.collect()
        b_list = flow_b.collect()
        uc_list = flow_uc.collect()

        for v in ["a", "a", "b", "c"]:
            c(v)

        assert a_list == ["a", "a"]
        assert b_list == ["b"]
        assert uc_list == ["c"]

    def test_no_unclassified_flow(self):
        c = Classificator(_value_is_class, ["a", "b"], False)
        flows = c.flows
        assert len(flows) == 2, "invalid number of flows created"

        flow_a, flow_b = flows
        a_list = flow_a.collect()
        b_list = flow_b.collect()

        for v in ["a", "a", "b", "c"]:
            c(v)  # no flow for "c"

        assert a_list == ["a", "a"]
        assert b_list == ["b"]

    def test_multiclass(self):
        def number_properties(n: int) -> list[str]:
            props = []
            if n % 2 == 0:
                props.append("even")
            else:
                props.append("odd")

            for d in range(2, 10):
                if n % d == 0:
                    props.append(f"div{d}")  # divisible by

            if n < 0:
                props.append("negative")

            return props

        c = Classificator(number_properties,
                          ["even", "negative", "div7"],
                          True)
        flows = c.flows
        assert len(flows) == 4, "invalid number of flows created"

        evens, negatives, div7s, rest = flows
        evens_list = evens.collect()
        negatives_list = negatives.collect()
        div7_list = div7s.collect()
        rest_list = rest.collect()

        c(4)  # evens
        c(-7)  # negatives, div7
        c(5)  # rest

        assert evens_list == [4]
        assert negatives_list == [-7]
        assert div7_list == [-7]
        assert rest_list == [5]
