from Jarvis import Jarvis

def test_recieves_temps():
    jarvis = Jarvis()
    temps = jarvis.get_temps()
    assert temps is not None
    assert jarvis.min_temp_24h != 0
    assert jarvis.max_temp_24h != 0
    assert jarvis.min_temp_week != 0
    assert jarvis.max_temp_week != 0