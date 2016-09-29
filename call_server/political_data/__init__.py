from countries import us, us_state


def load_data(cache):
    us_data = us.USData(cache)
    us_state_data = us_state.USStateData(cache)

    n = 0
    n += us_data.load_data()
    n += us_state_data.load_data()
    return n
