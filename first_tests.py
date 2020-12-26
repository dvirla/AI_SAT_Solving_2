import time
import ex2


def timeout_exec(func, args=(), kwargs={}, timeout_duration=10, default=None):
    """This function will spawn a thread and run the given function
    using the args, kwargs and return the given default value if the
    timeout_duration is exceeded.
    """
    import threading

    class InterruptableThread(threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)
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


def solve_problems(problems):
    for problem in problems:
        timeout = 300
        t1 = time.time()
        result = timeout_exec(ex2.solve_problem, args=[problem], timeout_duration=timeout)
        t2 = time.time()
        print(f'Your answer is {result}, achieved in {t2 - t1:.3f} seconds')


def main():
    print(ex2.ids)
    """Here goes the input you want to check"""
    problems = [
        {
            "police": 0,
            "medics": 0,
            "observations": [
                (
                    ('H', '?'),
                    ('H', 'H')
                ),

                (
                    ('S', '?'),
                    ('?', 'S')
                ),
            ],

            "queries": [
                ((0, 1), 0, "H"), ((1, 0), 1, "S")
            ]
        },

        {
            "police": 1,
            "medics": 0,
            "observations": [
                (
                    ('H', 'S'),
                    ('?', 'H')
                ),

                (
                    ('S', '?'),
                    ('?', 'S')
                ),
            ],

            "queries": [
                ((0, 1), 1, "H"), ((1, 0), 1, "S")
            ]

        }

    ]
    solve_problems(problems)


if __name__ == '__main__':
    main()