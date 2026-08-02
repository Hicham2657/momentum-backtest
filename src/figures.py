"""Figures for the project."""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

from data import build_dataset, load_average_firm_size, load_decile_returns

GREY, RED, GREEN, BLUE = '#B4B2A9', '#D85A30', '#1D9E75', '#185FA5'
OUTDIR = Path(__file__).resolve().parent.parent / 'figures'
OUTDIR.mkdir(exist_ok=True)


def _decile_colors():
    """Grey for the middle deciles, Red for LO and Green for HI."""
    colors = [GREY] * 10
    colors[0] = RED
    colors[9] = GREEN
    return colors


def plot_decile_returns(deciles):
    means = deciles.mean() * 100
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(range(10), means.values, color=_decile_colors(),
           edgecolor='black', linewidth=0.5)
    ax.axhline(means[1:9].mean(), color='#5F5E5A', linestyle='--',
               linewidth=1, label='Deciles 2-9 average')
    ax.axhline(0, color='black', linewidth=0.8)
    ax.set_xticks(range(10))
    ax.set_xticklabels(means.index, rotation=45, ha='right')
    ax.set_xlabel('Momentum decile')
    ax.set_ylabel('Mean monthly return (%)')
    ax.set_title('Decile returns')
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUTDIR / 'decile_returns.png', dpi=150)
    return fig


def plot_average_firm_size(size):
    means = size.mean()
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(range(10), means.values, color=_decile_colors(),
           edgecolor='black', linewidth=0.5)
    ax.set_yscale('log')
    ax.set_yticks([500, 1000, 2000, 5000])
    ax.get_yaxis().set_major_formatter(
        plt.FuncFormatter(lambda v, _: f'{v:,.0f}')
    )
    ax.set_xticks(range(10))
    ax.set_xticklabels(means.index, rotation=45, ha='right')
    ax.set_xlabel('Momentum decile')
    ax.set_ylabel('Average firm size ($m, log scale)')
    ax.set_title('The short leg holds the smallest firms')
    for i, value in enumerate(means.values):
        ax.text(i, value * 1.08, f'{value:,.0f}', ha='center', fontsize=8)
    fig.tight_layout()
    fig.savefig(OUTDIR / 'average_firm_size.png', dpi=150)
    return fig


def plot_cumulative(returns):
    cumulative = (1 + returns).cumprod()
    crash = pd.Timestamp('2009-04-01')
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(cumulative.index, cumulative.values, color=BLUE, linewidth=1)
    ax.set_yscale('log')
    ax.axvspan(pd.Timestamp('2008-09-01'), pd.Timestamp('2009-12-01'),
               color=RED, alpha=0.15)
    ax.annotate('April 2009: -45.2% in one month',
                xy=(crash, cumulative.at[crash]),
                xytext=(0.55, 0.25), textcoords='axes fraction',
                arrowprops=dict(arrowstyle='->', color='#5F5E5A'), fontsize=9)
    ax.set_ylabel('Growth (log scale)')
    ax.set_title('Cumulative gross performance, HI minus LO')
    fig.tight_layout()
    fig.savefig(OUTDIR / 'cumulative_performance.png', dpi=150)
    return fig

if __name__ == '__main__':
    plot_decile_returns(load_decile_returns())
    plot_average_firm_size(load_average_firm_size())
    plot_cumulative(build_dataset()['strategy'])
    plt.show()