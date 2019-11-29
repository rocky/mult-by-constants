from mult_by_const import MultConst
import os


def test_mult_cache():
    debug = "DEBUG" in os.environ
    m = MultConst(debug=debug)

    for clear_cache in (False, ):
        for n in range(340, 344):
            cost, instrs = m.find_mult_sequence(n)
            m.mult_cache.check()
            if clear_cache:
                m.mult_cache.clear()


# If run as standalone
if __name__ == "__main__":
    test_mult_cache()
