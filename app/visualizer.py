import matplotlib.pyplot as plt


def plot_histogram(data, title="Histogram"):
    plt.figure(figsize=(6, 4))
    plt.hist(data, bins=10)
    plt.title(title)
    plt.tight_layout()
    return plt
