from Jarvis import Jarvis

def test_recieves_temps():
    jarvis = Jarvis()
    temps = jarvis.get_temps()
    assert True