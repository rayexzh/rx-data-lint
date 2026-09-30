"""Render two reproducible, single-month figures from analysis exports.

Optional dependency: python -m pip install -r analysis/requirements-charts.txt
The core analysis and desktop checker do not depend on matplotlib.
"""
import argparse
import csv
import json
from decimal import Decimal
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter


def selected_row(path, month):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = [r for r in csv.DictReader(handle) if r["month"] == month]
    if len(rows) != 1:
        raise ValueError(f"Expected exactly one row for {month} in {path.name}")
    return rows[0]


def render(folder, month, output):
    meta = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    if month not in meta["months"]:
        raise ValueError("Requested month is not in the run manifest")
    coverage = selected_row(folder / "01_monthly_overview.csv", month)
    costs = selected_row(folder / "05_cost_sensitivity.csv", month)
    total = int(coverage["records"])
    counts = [int(coverage[k]) for k in ("known_cost_records", "missing_cost_records", "invalid_cost_records")]
    if total <= 0 or sum(counts) != total or int(costs["records"]) != total:
        raise ValueError("Summary counts do not reconcile")
    if not costs["known_net_indicative_cost_gbp"] or not costs["nonnegative_only_cost_gbp"]:
        raise ValueError("Costs unavailable: cannot draw cost comparison")
    net = Decimal(costs["known_net_indicative_cost_gbp"])
    nonnegative = Decimal(costs["nonnegative_only_cost_gbp"])
    negative = Decimal(costs["negative_component_gbp"])
    if abs(net - nonnegative - negative) > Decimal("0.02"):
        raise ValueError("Cost components do not reconcile within rounding tolerance")
    output.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 12,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "axes.spines.left": False, "axes.spines.bottom": False})
    footer = f"Source: NHSBSA provisional SCMD | {month} | OGL v3.0 | Independent RxDataLint analysis"

    fig, ax = plt.subplots(figsize=(12, 6.5), facecolor="#f7f9f8")
    fig.subplots_adjust(left=.08, right=.95, top=.68, bottom=.30)
    ax.set_facecolor("#f7f9f8")
    fig.text(.08,.91,"How complete are the cost records?", fontsize=23, weight="bold", color="#153f36")
    fig.text(.08,.83,f"{month}  /  {total:,} records  /  completeness by record count", color="#52635d")
    colors = ["#176b58", "#df9b31", "#aa4148"]
    left = 0
    for count, color in zip(counts, colors):
        percentage = 100 * count / total
        ax.barh([0], [percentage], left=left, height=.42, color=color)
        left += percentage
    ax.set_xlim(0,100)
    ax.set_ylim(-.7,.7)
    ax.set_yticks([])
    ax.set_xticks([0,25,50,75,100], ["0%","25%","50%","75%","100%"])
    ax.tick_params(axis="x", length=0, colors="#52635d")
    for x, label, count, color in zip([.08,.40,.72],["Known cost","Missing cost","Invalid nonblank cost"],counts,colors):
        fig.text(x,.24,label,color=color,weight="bold",fontsize=12)
        fig.text(x,.18,f"{count:,}  ({count/total:.2%})",fontsize=17,color="#24352e")
    fig.text(.08,.10,"Missing costs remain unavailable. This percentage is not coverage by expenditure.",fontsize=10,color="#52635d")
    fig.text(.08,.045,footer,fontsize=9,color="#52635d")
    for suffix in ("png","svg"):
        fig.savefig(output / f"cost_completeness.{suffix}",dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(12,6.5),facecolor="#f7f9f8")
    fig.subplots_adjust(left=.26,right=.95,top=.68,bottom=.30)
    ax.set_facecolor("#f7f9f8")
    fig.text(.08,.91,"What changes when negative costs are removed?",fontsize=21,weight="bold",color="#153f36")
    delta = nonnegative-net
    fig.text(.08,.82,f"{month}  /  {int(costs['negative_cost_records']):,} negative-cost records",color="#52635d")
    values = [float(net)/1e6,float(nonnegative)/1e6]
    ax.barh([1,0],values,height=.45,color=["#176b58","#df9b31"])
    ax.set_yticks([1,0],["Including negatives","Excluding negatives\n(hypothetical)"])
    # Include zero and accommodate negative net totals for other supported files.
    ax.set_xlim(min(0,min(values)*1.12),max(1,max(values)*1.23))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda value,pos:f"{value:,.0f}"))
    ax.set_xlabel("Known indicative cost (GBP millions)",color="#52635d")
    ax.tick_params(length=0)
    for y,value in zip([1,0],values):
        ax.text(value,y,f"  £{value:,.2f}m",va="center",fontsize=12,weight="bold")
    fig.text(.08,.19,f"Change in the sum: +£{delta:,.2f}",fontsize=18,weight="bold",color="#153f36")
    fig.text(.08,.115,"Illustrates a cleaning decision, not a recommendation to remove negatives.",fontsize=10,color="#52635d")
    fig.text(.08,.08,"Missing costs excluded from both sums. Indicative cost is not actual procurement expenditure.",fontsize=10,color="#52635d")
    fig.text(.08,.035,footer,fontsize=9,color="#52635d")
    for suffix in ("png","svg"):
        fig.savefig(output / f"negative_cost_impact.{suffix}",dpi=160)
    plt.close(fig)
    (output / "figures_manifest.json").write_text(json.dumps({
        "month":month,"source_sha256":meta["source_sha256"],"source_url":meta["source_url"],
        "matplotlib_version":matplotlib.__version__,"coverage":coverage,"costs":costs
    },indent=2),encoding="utf-8")


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder",type=Path,help="Completed analysis output folder")
    parser.add_argument("--month",required=True,help="YYYY-MM")
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    render(args.folder,args.month,args.output)
    print(f"Figures saved to {args.output.resolve()}")
