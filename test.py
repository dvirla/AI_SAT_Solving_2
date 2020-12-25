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


def solve_problems(problems, expected_output):
    for problem, expected in zip(problems, expected_output):
        timeout = 300
        t1 = time.time()
        result = timeout_exec(ex2.solve_problem, args=[problem], timeout_duration=timeout)
        t2 = time.time()
        print(f'Your answer is {result}, achieved in {t2 - t1:.3f} seconds')
        print('Expected output is: ' + str(expected))
        if expected == result: print('Correct!')
        else: print('Wrong!')
        print('\n')


def main():
    print(ex2.ids)
    """Here goes the input you want to check"""
    problems = [
        {
            "police": 0,
            "medics": 0,
            "observations": [
                (
                    ('H', '?', 'H'),
                    ('H', 'H', 'H'),
                    ('H', 'H', 'S'),
                ),

                (
                    ('H', 'H', 'H'),
                    ('?', 'H', 'S'),
                    ('H', 'S', 'S'),
                ),

                (
                    ('H', 'H', 'S'),
                    ('H', '?', 'S'),
                    ('S', 'S', 'S'),
                ),

                (
                    ('?', 'S', 'S'),
                    ('S', 'S', 'S'),
                    ('S', 'S', 'H'),
                ),
            ],

            "queries": [
                ((0, 1), 0, 'H'), ((1, 0), 1, 'S'), ((1, 1), 2, 'H'), ((0, 0), 3, 'S')
            ],

        },

        {
            "police": 1,
            "medics": 0,
            "observations": [
                (
                    ('S', 'H', 'U'),
                    ('H', 'H', 'H'),
                    ('U', 'H', 'S'),
                ),

                (
                    ('S', 'S', 'U'),
                    ('S', 'H', 'S'),
                    ('U', 'S', '?'),
                ),

                (
                    ('?', 'S', 'U'),
                    ('S', 'S', 'S'),
                    ('U', 'S', 'Q'),
                ),
            ],

            "queries": [
                ((0, 0), 2, 'H')
            ],

        },

        {
            "police": 0,
            "medics": 0,
            "observations": [
                (
                    ('H', 'H', 'H', 'H'),
                    ('H', 'S', 'U', 'H'),
                    ('H', 'H', 'H', '?'),
                    ('H', 'H', 'S', 'S'),
                ),

                (
                    ('H', 'S', 'H', 'H'),
                    ('S', 'S', 'U', 'H'),
                    ('H', 'S', 'S', 'U'),
                    ('?', 'S', 'S', 'S'),
                ),
            ],

            "queries": [
                ((2, 3), 0, 'H'), ((3, 0), 1, 'H')
            ],
        },

        {
            "police": 0,
            "medics": 1,
            "observations": [
                (
                    ('H', 'H', 'H', 'H'),
                    ('H', 'S', 'U', 'H'),
                    ('U', 'S', 'S', 'U'),
                    ('H', 'S', 'H', 'H'),
                ),

                (
                    ('H', 'S', 'H', 'I'),
                    ('S', 'S', 'U', 'H'),
                    ('U', '?', 'S', 'U'),
                    ('S', 'S', 'S', 'H'),
                ),

                (
                    ('S', 'S', 'I', 'I'),
                    ('S', 'S', 'U', '?'),
                    ('U', 'S', 'S', 'U'),
                    ('?', 'S', 'S', 'S')
                ),

            ],

            "queries": [
                ((2, 1), 1, 'U'), ((1, 3), 2, 'I'), ((3, 0), 2, 'S')
            ],
        },

        {
            "police": 0,
            "medics": 0,
            "observations": [
                (
                    ('H', 'S'),
                    ('H', 'H'),
                ),

                (
                    ('S', 'S'),
                    ('H', 'S'),
                ),

                (
                    ('S', 'S'),
                    ('S', 'S'),
                ),

                (
                    ('S', 'H'),
                    ('S', 'S'),
                ),

                (
                    ('?', '?'),
                    ('?', '?'),
                ),

            ],

            "queries": [
                ((0, 0), 4, 'H'), ((1, 0), 4, 'S')
            ],
        },

    ]
    # problems = [
    #     {
    #         "police": 0,
    #         "medics": 0,
    #         "observations": [
    #             (
    #                 ('H', '?'),
    #                 ('H', 'H')
    #             ),
    #
    #             (
    #                 ('S', '?'),
    #                 ('?', 'S')
    #             ),
    #         ],
    #
    #         "queries": [
    #             [((0, 1), 0, "H"), ((1, 0), 1, "S")]
    #         ]
    #     },
    #
    #     {
    #         "police": 1,
    #         "medics": 0,
    #         "observations": [
    #             (
    #                 ('H', 'S'),
    #                 ('?', 'H')
    #             ),
    #
    #             (
    #                 ('S', '?'),
    #                 ('?', 'S')
    #             ),
    #         ],
    #
    #         "queries": [
    #             [((0, 1), 1, "H"), ((1, 0), 1, "S")]
    #         ]
    #
    #     },
    #
    #     {
    #         "police": 0,
    #         "medics": 1,
    #         "observations": [
    #             (
    #                 ('H', 'S'),
    #                 ('H', 'H')
    #             ),
    #
    #             (
    #                 ('S', 'S'),
    #                 ('?', 'S')
    #             ),
    #
    #             (
    #                 ('S', '?'),
    #                 ('?', 'S')
    #             ),
    #
    #             (
    #                 ('S', '?'),
    #                 ('?', 'S')
    #             ),
    #         ],
    #
    #         "queries": [
    #             [((1, 0), 1, "H"), ((1, 0), 1, "Q"), ((1, 0), 1, "S"), ((1, 0), 1, "U"),
    #              ((1, 0), 1, "I")]
    #         ]
    #
    #     },
    #
    #     {
    #         "police": 0,
    #         "medics": 1,
    #         "observations": [
    #             (
    #                 ('H', 'S'),
    #                 ('H', 'H')
    #             ),
    #
    #             (
    #                 ('S', '?'),
    #                 ('?', 'S')
    #             ),
    #
    #             (
    #                 ('S', '?'),
    #                 ('?', 'S')
    #             ),
    #
    #             (
    #                 ('S', '?'),
    #                 ('?', 'S')
    #             ),
    #         ],
    #
    #         "queries": [
    #             [((0, 1), 2, "Q"), ((0, 1), 2, "H"), ((0, 1), 2, "S"),
    #              ((0, 1), 2, "U"), ((0, 1), 2, "I")]
    #         ]
    #
    #     }
    # ]

    expected_output = [
        {
            ((0, 1), 0, "H"): 'F',
            ((1, 0), 1, "S"): 'F'
        },

        {
            ((0, 1), 1, "H"): 'F',
            ((1, 0), 1, "S"): '?'
        },

        {
            ((1, 0), 1, "H"): 'F',
            ((1, 0), 1, "Q"): 'F',
            ((1, 0), 1, "S"): 'F',
            ((1, 0), 1, "U"): 'F',
            ((1, 0), 1, "I"): 'T'
        },

        {
            ((0, 1), 2, "Q"): 'F',
            ((0, 1), 2, "H"): 'F',
            ((0, 1), 2, "S"): 'T',
            ((0, 1), 2, "U"): 'F',
            ((0, 1), 2, "I"): 'F'
        }
    ]
    solve_problems(problems[1:], expected_output[1:5])


if __name__ == '__main__':
    main()
