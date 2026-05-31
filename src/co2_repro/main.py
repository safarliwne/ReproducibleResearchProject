from src.co2_repro.data import load_data
from src.co2_repro.visualization import plot_world_co2


def main():
    df = load_data()
    plot_world_co2(df)
    print("Analysis completed. Plot saved in reports folder.")


if __name__ == "__main__":
    main()
