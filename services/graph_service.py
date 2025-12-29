import seaborn as sns
import matplotlib.pyplot as plt

def plot_graph(df, graph_type, cols, title=None):
    plt.figure(figsize=(6, 4))

    if graph_type == "line":
        for c in cols:
            plt.plot(df["month"], df[c], label=c)
        plt.legend()

    elif graph_type == "bar":
        df.plot(x="month", y=cols, kind="bar")

    elif graph_type == "area":
        df.plot(x="month", y=cols, kind="area")

    elif graph_type == "hist":
        df[cols[0]].plot(kind="hist")

    elif graph_type == "box":
        sns.boxplot(data=df[cols])

    elif graph_type == "violin":
        sns.violinplot(data=df[cols])

    elif graph_type == "grouped_bar":
        df.plot(x="month", y=cols, kind="bar")

    elif graph_type == "multi_line":
        for c in cols:
            plt.plot(df["month"], df[c], label=c)
        plt.legend()

    elif graph_type == "area_stack":
        df.plot(x="month", y=cols, kind="area", stacked=True)

    elif graph_type == "heatmap":
        sns.heatmap(df[cols].corr(), annot=True, cmap="coolwarm")

    elif graph_type == "pairplot":
        sns.pairplot(df[cols])

    if title:
        plt.title(title, fontsize=11, fontweight="bold")

    plt.tight_layout()
