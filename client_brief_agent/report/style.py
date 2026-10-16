"""matplotlib look that matches the web page (light tokens from the fraud page)."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from client_brief_agent import config

INK = "#141A34"
INK_SOFT = "#464E6E"
SLATE = "#6C7492"
BLUE = "#2C3696"
BLUE_SOFT = "#7982D0"
BLUE_WASH = "#DEE3F5"
FLAG = "#F76300"
AMBER = "#C77A12"
PAPER = "#FFFFFF"
RULE = "#D9DCE6"

# cluster colours: blue first, orange kept for things that need attention
CLUSTER_COLOURS = ["#2C3696", "#7982D0", "#C77A12", "#3E8E7E", "#8A93C4",
                   "#1B2160", "#B08BBB", "#6C7492", "#A3B86C", "#4F6DB8"]


def apply():
    plt.rcParams.update({
        "figure.dpi": 100,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "figure.facecolor": PAPER,
        "axes.facecolor": PAPER,
        "axes.edgecolor": RULE,
        "axes.labelcolor": INK_SOFT,
        "axes.titlecolor": BLUE,
        "axes.titleweight": "bold",
        "axes.titlesize": 12,
        "axes.titlelocation": "left",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.color": RULE,
        "grid.linewidth": 0.6,
        "xtick.color": SLATE,
        "ytick.color": SLATE,
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "legend.frameon": False,
    })


def save(fig, name):
    """every figure goes to outputs/figures and a copy next to the page."""
    config.FIG_DIR.mkdir(parents=True, exist_ok=True)
    config.DOCS_FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(config.FIG_DIR / f"{name}.png")
    fig.savefig(config.DOCS_FIG_DIR / f"{name}.png", dpi=150)
    plt.close(fig)
    return f"figures/{name}.png"
