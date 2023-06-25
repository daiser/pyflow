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
