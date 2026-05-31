from data import load_data
from visualization import plot_world_co2


def main():
    df = load_data()
    plot_world_co2(df)
    print("Analysis completed. Plot saved in reports folder.")


if __name__ == "__main__":
    main()
