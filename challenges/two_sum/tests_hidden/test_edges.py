from starter import two_sum

def test_negative():
    res = two_sum([-1,-2,-3,-4,-5], -8)
    assert res == [2,4]
