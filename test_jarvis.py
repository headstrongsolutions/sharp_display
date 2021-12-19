from Jarvis import Jarvis

def test_recieves_temps():
    jarvis = Jarvis()
    temps = jarvis.get_temps()
    assert temps is not None
    assert jarvis.min_temp != 0
    assert jarvis.max_temp != 0