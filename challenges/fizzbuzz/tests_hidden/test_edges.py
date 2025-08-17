from starter import fizzbuzz

def test_large():
    out = fizzbuzz(100)
    assert out[2] == "Fizz" and out[4] == "Buzz" and out[14] == "FizzBuzz"
