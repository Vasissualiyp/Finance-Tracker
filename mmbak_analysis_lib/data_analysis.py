
import matplotlib.pyplot as plt

def plot_data(df, title, x_col, y_col, log_scale=False):
    """
    Plot the data from a DataFrame.

    Args:
    df (DataFrame): The pandas DataFrame containing the data to plot.
    title (str): The title of the plot.
    x_col (str): The column name for the x-axis.
    y_col (str): The column name for the y-axis.
    log_scale (bool): Whether to use a logarithmic scale for the y-axis.
    """
    plt.figure(figsize=(12, 6))
    plt.plot(df[x_col], df[y_col].astype(float), marker='o')
    plt.xlabel(x_col)
    plt.ylabel(y_col)
    if log_scale:
        plt.yscale('log')
    plt.title(title)
    plt.grid(True)
    plt.show()
