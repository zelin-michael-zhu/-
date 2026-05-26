from app.services.matching.gpa_converter import convert_to_4


def test_convert_4_scale():
    assert convert_to_4(3.62, 4.0) == 3.62


def test_convert_5_scale():
    assert convert_to_4(4.5, 5.0) == 3.6


def test_convert_100_scale():
    assert convert_to_4(88, 100) == 3.7
    assert convert_to_4(59, 100) == 0
