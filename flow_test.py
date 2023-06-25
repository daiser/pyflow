from flow import Flow


class TestFlow:
    def test_filter(self):
        flow = Flow[int]()
        evens = flow.filter(lambda n: n % 2 == 0).collect()
        flow.send([1, 2, 3, 4])

        assert evens == [2, 4]

    def test_collect(self):
        flow = Flow[str]()
        strings = flow.collect()
        flow("a")
        flow("b")
        flow("c")
        assert strings == ["a", "b", "c"]

    def test_collect_to(self):
        my_list = []
        flow = Flow[int]()
        flow.collect_to(my_list)
        flow(1)
        flow.send([2, 3])
        assert my_list == [1, 2, 3]

    def test_peep(self):
        peeped = []
        flow = Flow[str]()
        flow.peep(lambda s: peeped.append(s))
        flow.send(["a", "b", "c"])
        assert peeped == ["a", "b", "c"]
