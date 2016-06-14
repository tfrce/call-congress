from countries import us, us_state


def load_data(cache):
    us_data = us.USData(cache)
    us_data.load_data()
    us_state_data = us_state.USStateData(cache)
    us_state_data.load_data()
