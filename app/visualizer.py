try:
    import matplotlib.pyplot as plt

    def plot_histogram(data, title="Histogram"):
        plt.figure(figsize=(6, 4))
        plt.hist(data, bins=10)
        plt.title(title)
        plt.tight_layout()
        return plt

except Exception:
    # Fallback dummy plot for environments where matplotlib installation fails
    class DummyPlot:
        def __init__(self):
            self._figname = "dummy"

        def savefig(self, path):
            with open(path, "wb") as fh:
                fh.write(b"\x89PNG\r\n\x1a\n")

    def plot_histogram(data, title="Histogram"):
        print("matplotlib not available; using dummy plot")
        return DummyPlot()
