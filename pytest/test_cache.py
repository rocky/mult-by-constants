from mult_by_const import MultConst
import os


def test_mult_cache():
    debug = "DEBUG" in os.environ
    m = MultConst(debug=debug)

    for clear_cache in (True, False):
        for n in range(340, 344):
            cost, instrs = m.find_mult_sequence(n)
            m.check_mult_cache()
            if clear_cache:
                m.clear_mult_cache()


# If run as standalone
if __name__ == "__main__":
    test_mult_cache()
