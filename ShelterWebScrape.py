import requests
from bs4 import BeautifulSoup


def get_order(place) -> dict:
    order = place.contents[1].contents[0]
    when = place.contents[1].contents[1].contents[0].split(" ")[2:4]
    date = " ".join(str(i) for i in when) + " 2020"
    return {"order": order, "date": date}


def get_counties(state) -> dict:
    orders = {}
    for county in state.find_all(attrs={"class": "place-wrap"}):
        name = county.contents[1].contents[0]
        pop = populations(county.contents[1].contents[1].contents[0].replace(",", "").split(" ")[1:-1])
        order = county.contents[3].contents[0]
        when = county.contents[3].contents[1].contents[0].split(" ")[2:4]
        date = " ".join(str(i) for i in when[:2]) + " 2020"
        orders[name] = {"order": order, "date": date, "pop": pop}
    return orders


def populations(pop):
    if len(pop) == 1:
        return int(pop[0])
    text2num = {"thousand": 1000,
                "million": 1000000}
    return int(float(pop[0]) * text2num[pop[1]])


def get_state_wraps():
    try:
        r = requests.get('https://www.nytimes.com/interactive/2020/us/coronavirus-stay-at-home-order.html')
    except requests.exceptions.MissingSchema:
        print("The supplied URL is invalid. Please update and run again.")
        raise Exception("InvalidURL")
    soup = BeautifulSoup(r.text, 'html.parser')
    return soup.find_all(attrs={"class": "state-wrap"})


def populate_states(state_wraps, save=True, rebuild=False):
    datafile = "Covid19ShelterOrders.csv"
    if not rebuild:
        try:
            return parse_data(datafile)
        except FileNotFoundError:
            print("Stored data cannot be found.", end=" ")

    print("Rebuilding...")

    states = {}
    for state_wrap in state_wraps:
        st = state_wrap.contents[1].next.strip(" ")
        if len(state_wrap.attrs["class"]) == 2:
            order = get_order(state_wrap.contents[5])
            order["pop"] = populations(state_wrap.contents[1].contents[1].contents[0].replace(",", "").split(" ")[1:-1])
            order = {"Statewide": order}
        else:
            order = get_counties(state_wrap)

        states[st] = order

    if save:
        with open(datafile, "w") as orders:
            orders.write("State, County, Population, Order, Date\n")
            for state, info in states.items():
                for county, order in info.items():
                    orders.write(state + ", " + county + ", " + str(order["pop"]) + ", "
                                 + order["order"] + ", " + order["date"] + "\n")
        print("Data written to", datafile)
    return states


def parse_data(filename):
    pass


def main():
    state_wraps = get_state_wraps()
    states = populate_states(state_wraps, )
    return states


if __name__ == "__main__":
    main()
