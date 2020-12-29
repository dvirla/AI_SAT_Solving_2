import time
import ex2


def timeout_exec(func, args=(), kwargs={}, timeout_duration=10, default=None):
    """This function will spawn a thread and run the given function
    using the args, kwargs and return the given default value if the
    timeout_duration is exceeded.
    """
    import threading

    class InterruptableThread(threading.Thread):
        def _init_(self):
            threading.Thread._init_(self)
            self.result = default

        def run(self):
            # remove try if you want program to abort at error
            # try:
            self.result = func(*args, **kwargs)
            # except Exception as e:
            #    self.result = (-3, -3, e)

    it = InterruptableThread()
    it.start()
    it.join(timeout_duration)
    if it.is_alive():
        return default
    else:
        return it.result


def text_5X5():
    problem = {
        "police": 2,
        "medics": 2,
        "observations": [
            (
                ('H', 'S', 'U', 'H', 'H', '?'),
                ('S', 'H', 'H', 'S', 'U', 'U'),
                ('?', 'H', 'H', 'U', 'S', 'U'),
                ('H', 'S', 'H', 'H', 'H', 'S'),
                ('H', 'H', '?', 'H', 'H', 'H'),
                ('H', 'H', 'H', 'S', 'H', 'U'),
            ),
            (
                ('S', 'S', 'U', 'I', 'H', '?'),
                ('S', 'I', 'S', 'S', 'U', 'U'),
                ('?', 'H', 'H', 'U', 'S', 'U'),
                ('H', 'Q', 'H', 'H', 'S', 'S'),
                ('H', 'H', '?', 'H', 'H', 'S'),
                ('H', 'H', 'H', 'Q', 'H', 'U'),
            ),
            (
                ('S', 'S', 'U', 'I', 'H', '?'),
                ('S', 'I', 'Q', 'S', 'U', 'U'),
                ('?', 'H', 'H', 'U', 'S', 'U'),
                ('H', 'Q', 'H', 'I', 'S', 'S'),
                ('H', 'H', '?', 'H', 'I', 'Q'),
                ('H', '?', 'H', 'Q', 'H', 'U'),
            ),
            (
                ('Q', 'H', 'U', 'I', 'H', '?'),
                ('H', 'I', 'Q', 'H', 'U', 'U'),
                ('?', 'H', 'H', 'U', 'H', 'U'),
                ('H', 'H', 'H', 'I', 'Q', 'H'),
                ('H', 'H', '?', 'H', 'I', '?'),
                ('H', 'H', 'I', '?', 'I', 'U'),
            ),
        ],
        "queries": [

            ((2, 0), 0, "Q"), ((2, 0), 0, "I"), ((2, 0), 0, "S"), ((2, 0), 0, "U"), ((2, 0), 0, "H"),
            ((0, 5), 0, "Q"), ((0, 5), 0, "I"), ((0, 5), 0, "S"), ((0, 5), 0, "U"), ((0, 5), 0, "H"),
            ((4, 2), 1, "Q"), ((4, 2), 1, "I"), ((4, 2), 1, "S"), ((4, 2), 1, "U"), ((4, 2), 1, "H"),
            ((5, 1), 2, "Q"), ((5, 1), 2, "I"), ((5, 1), 2, "S"), ((5, 1), 2, "U"), ((5, 1), 2, "H"),
            ((5, 3), 3, "Q"), ((5, 3), 3, "I"), ((5, 3), 3, "S"), ((5, 3), 3, "U"), ((5, 3), 3, "H"),
            ((4, 5), 3, "Q"), ((4, 5), 3, "I"), ((4, 5), 3, "S"), ((4, 5), 3, "U"), ((4, 5), 3, "H")
        ]
    }
    timeout = 3000
    t1 = time.time()
    result = timeout_exec(ex2.solve_problem, args=[problem], timeout_duration=timeout)
    t2 = time.time()

    expected = {
        ((2, 0), 0, "Q"): 'F',
        ((2, 0), 0, "I"): 'F',
        ((2, 0), 0, "S"): 'F',
        ((2, 0), 0, "U"): 'T',
        ((2, 0), 0, "H"): 'F',

        ((0, 5), 0, "Q"): 'F',
        ((0, 5), 0, "I"): 'F',
        ((0, 5), 0, "S"): 'F',
        ((0, 5), 0, "U"): '?',
        ((0, 5), 0, "H"): '?',

        ((4, 2), 1, "Q"): 'F',
        ((4, 2), 1, "S"): 'F',
        ((4, 2), 1, "I"): 'F',
        ((4, 2), 1, "H"): '?',
        ((4, 2), 1, "U"): '?',

        ((5, 1), 2, "Q"): 'F',
        ((5, 1), 2, "I"): 'F',
        ((5, 1), 2, "S"): 'F',
        ((5, 1), 2, "U"): 'F',
        ((5, 1), 2, "H"): 'T',

        ((5, 3), 3, "Q"): 'F',
        ((5, 3), 3, "I"): 'F',
        ((5, 3), 3, "S"): 'F',
        ((5, 3), 3, "U"): 'F',
        ((5, 3), 3, "H"): 'T',

        ((4, 5), 3, "Q"): 'T',
        ((4, 5), 3, "I"): 'F',
        ((4, 5), 3, "S"): 'F',
        ((4, 5), 3, "U"): 'F',
        ((4, 5), 3, "H"): 'F'

    }

    total = 0

    num_of_mistakes = 0
    print('Test 1 Results:')
    for query, res in result.items():
        if res != expected[query]:
            print('query: {} , your res: {} , expected res: {}'.format(query, res, expected[query]))
            num_of_mistakes += 1
        total += 1

    print('{} mistakes out of {}'.format(num_of_mistakes, total))


def test_8X8_2():
    problem = {
        "police": 3,
        "medics": 3,
        "observations": [
            (('S', 'H', 'H', 'H', 'H', 'U', 'U', 'H'),
             ('U', 'U', 'H', 'H', 'S', 'U', 'U', 'H'),
             ('U', '?', 'H', 'H', 'H', 'U', 'H', 'H'),
             ('U', 'H', 'H', 'H', 'U', 'U', 'H', 'S'),
             ('U', 'H', 'H', 'H', 'H', 'H', 'U', '?'),
             ('U', 'H', 'H', 'S', '?', 'S', 'H', 'H'),
             ('S', 'H', 'U', 'H', 'H', 'U', 'U', 'H'),
             ('U', 'H', 'U', 'H', 'U', 'H', 'U', 'U')),

            (('Q', 'H', 'H', 'H', 'S', 'U', 'U', 'H'),
             ('U', 'U', 'H', 'I', 'S', 'U', 'U', 'H'),
             ('U', '?', 'H', 'H', 'S', 'U', 'H', 'S'),
             ('U', 'H', 'H', 'H', 'U', 'U', 'S', 'S'),
             ('U', 'H', 'H', 'S', 'H', 'H', 'U', '?'),
             ('U', 'H', 'I', 'S', '?', 'Q', 'H', 'H'),
             ('Q', 'H', 'U', 'I', 'H', 'U', 'U', 'H'),
             ('U', 'H', 'U', 'H', 'U', 'H', 'U', 'U')),

        ],
        "queries": [[

            ((2, 1), 0, "Q"), ((2, 1), 0, "I"), ((2, 1), 0, "S"), ((2, 1), 0, "U"), ((2, 1), 0, "H"),
            ((5, 4), 1, "Q"), ((5, 4), 1, "I"), ((5, 4), 1, "S"), ((5, 4), 1, "U"), ((5, 4), 1, "H"),
            ((4, 7), 1, "Q"), ((4, 7), 1, "I"), ((4, 7), 1, "S"), ((4, 7), 1, "U"), ((4, 7), 1, "H"),

        ]]
    }
    timeout = 30000
    t1 = time.time()
    result = timeout_exec(ex2.solve_problem, args=[problem], timeout_duration=timeout)
    t2 = time.time()
    print(f'Your answer is {result}, achieved in {t2 - t1:.3f} seconds')

    assert result[((2, 1), 0, "Q")] == 'F'
    assert result[((2, 1), 0, "I")] == 'F'
    assert result[((2, 1), 0, "S")] == 'F'
    assert result[((2, 1), 0, "U")] == '?'
    assert result[((2, 1), 0, "H")] == '?'

    assert result[((4, 7), 1, "Q")] == 'F'
    assert result[((4, 7), 1, "I")] == 'F'
    assert result[((4, 7), 1, "S")] == '?'
    assert result[((4, 7), 1, "U")] == '?'
    assert result[((4, 7), 1, "H")] == 'F'

    assert result[((5, 4), 1, "Q")] == 'F'
    assert result[((5, 4), 1, "S")] == '?'
    assert result[((5, 4), 1, "I")] == 'F'
    assert result[((5, 4), 1, "H")] == 'F'
    assert result[((5, 4), 1, "U")] == '?'


def main():
    text_5X5()  # alexa's assertions are the correct answers.
    # test_8X8_2() # alexa's assertions are the correct answers

    '''
    to test our code uncomment the assertions from each test body.
    if an assertion error is thrown - he haven't passed a certain query.
    '''


if __name__ == '__main__':
    main()