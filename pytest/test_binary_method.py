from mult_by_const import MultConst


def test_binary_method():
    m = MultConst(debug=False)
    for (n, expect) in (
        (0, 0),
        (1, 0),
        (2, 1),
        (3, 2),
        (4, 1),
        (5, 2),
        (6, 3),
        (7, 2),
        (8, 1),
        (53, 6),
    ):
        cost, result = m.binary_sequence(n)
        assert expect == cost, f"cost({n}) = {cost}; expected it to be {expect}."
