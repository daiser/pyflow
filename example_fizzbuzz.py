from flow import Flow


def fizzbuzzer(n: int) -> str:
    if n % 15 == 0:
        return 'fb'
    if n % 3 == 0:
        return 'f'
    if n % 5 == 0:
        return 'b'
    return 'n'


flow = Flow[int]()

fizzbuzz, fizz, buzz, num, _ = flow.segregate(fizzbuzzer, 'fb', 'f', 'b', 'n')

fizzbuzz.peep(lambda n: print("FizzBuzz"))
fizz.peep(lambda n: print("Fizz"))
buzz.peep(lambda n: print("Buzz"))
num.peep(print)

flow.send(range(1, 101))
