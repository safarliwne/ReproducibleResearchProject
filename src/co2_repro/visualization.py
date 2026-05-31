import matplotlib.pyplot as plt


def plot_world_co2(df):
    """
    Plot global CO2 emissions over time.
    """
    world = df[df["country"] == "World"]

    plt.figure(figsize=(10, 6))
    plt.plot(world["year"], world["co2"])
    plt.title("Global CO2 Emissions Over Time")
    plt.xlabel("Year")
    plt.ylabel("CO2 Emissions")
    plt.grid(True)

    plt.savefig("reports/global_co2_trend.png")
    plt.close()
