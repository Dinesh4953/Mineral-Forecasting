from flask import Flask, render_template, request, send_file
import io
import pandas as pd
import matplotlib.pyplot as plt
import os
import uuid

from commodity_countries import get_country_data
from services.detailed_service import get_detailed_data
app = Flask(__name__)


PLOT_DIR = "static/plots"
os.makedirs(PLOT_DIR, exist_ok=True)


def is_numeric(values):
    numeric = pd.to_numeric(pd.Series(values), errors="coerce")
    return numeric.notna().all()


def is_chart_valid(chart_type, values, countries):
    if not is_numeric(values):
        return False, "Selected column is not numeric"

    if chart_type == "pie" and len(values) > 15:
        return False, "Pie chart supports max 15 categories"

    if chart_type == "line" and len(values) < 2:
        return False, "Line chart needs multiple data points"

    if chart_type == "scatter" and len(values) < 2:
        return False, "Scatter chart needs multiple data points"

    if chart_type == "area" and len(values) < 2:
        return False, "Area chart needs multiple data points"

    return True, None




def generate_chart(countries, values, label, chart_type):

    valid, reason = is_chart_valid(chart_type, values, countries)

    if not valid:
        return None, reason   

    plt.figure(figsize=(10, 6))

    if chart_type == "bar":
        plt.barh(countries, values)

    elif chart_type == "line":
        plt.plot(countries, values, marker="o")
        plt.xticks(rotation=90)

    elif chart_type == "pie":
        plt.pie(values, labels=countries, autopct="%1.1f%%")
        
    elif chart_type == "scatter":
        plt.scatter(countries, values)
        plt.xticks(rotation=90)

    elif chart_type == "vbar":
        plt.bar(countries, values)
        plt.xticks(rotation=90)

    elif chart_type == "area":
        plt.fill_between(range(len(values)), values)
        plt.xticks(range(len(countries)), countries, rotation=90)

    plt.title(f"{label} Distribution")

    filename = f"chart_{uuid.uuid4().hex}.png"
    path = os.path.join(PLOT_DIR, filename)

    plt.tight_layout()
    plt.savefig(path)
    plt.close()

    return path, None


# ---------------- LANDING PAGE ----------------
@app.route("/")
def index():
    return render_template("index.html")


# ---------------- COMMODITY → COUNTRIES ----------------
@app.route("/countries", methods=["GET", "POST"])
def countries():

    metric = request.form.get("metric", "Quantity")
    trade = request.form.get("trade", "Export")
    year = request.form.get("year", "2017")
    commodity = request.form.get("commodity", "28252000")
    row_limit = int(request.form.get("row_limit", 10))
    chart_type = request.form.get("chart_type", "bar")

    selected_columns = request.form.getlist("columns")

    # 1️⃣ Get full country data
    df, label, _, _ = get_country_data(
        metric=metric,
        trade_type=trade,
        year=year,
        commodity=commodity,
    )

    # 2️⃣ Separate TOTAL
    total_row = df[df["Country"] == "TOTAL"]
    data_rows = df[df["Country"] != "TOTAL"]

    # 3️⃣ SORT FIRST (CRITICAL FIX)
    data_rows = data_rows.sort_values(label, ascending=False)

    # 4️⃣ Apply Top-N
    if row_limit > 0:
        data_rows = data_rows.head(row_limit)

    # 5️⃣ Prepare chart data
    countries_list = data_rows["Country"].tolist()
    values = data_rows[label].tolist()

    # 6️⃣ Generate chart
    chart_path, chart_error = generate_chart(
        countries_list,
        values,
        label,
        chart_type
    )

    # 7️⃣ Re-append TOTAL for table
    df = pd.concat([data_rows, total_row], ignore_index=True)

    # 8️⃣ Apply column selection
    if selected_columns:
        keep_cols = ["Country"] + [c for c in selected_columns if c in df.columns]
        df = df[keep_cols]

    return render_template(
        "countries.html",
        metric=metric,
        trade=trade,
        year=year,
        commodity=commodity,
        label=label,
        table=df.to_dict("records"),
        row_limit=row_limit,
        selected_columns=selected_columns,
        chart_type=chart_type,
        chart_path=chart_path,
        chart_error=chart_error
    )

from flask import render_template, request
from services.detailed_service import get_detailed_data
from services.graph_rules import get_valid_graphs   # ✅ NEW
import pandas as pd
import os


# ---------------- SAFE INT ----------------
def safe_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


@app.route("/detailed", methods=["GET", "POST"])
def detailed():

    # ---------------- TOP FILTER ----------------
    mineral = request.form.get("mineral", "Lithium")
    trade = request.form.get("trade", "Export")
    selected_months = request.form.getlist("months")
    selected_columns = request.form.getlist("columns") or None

    table_file_path = f"Data/{mineral}/{mineral.lower()}_{trade.lower()}.xlsx"

    if not os.path.exists(table_file_path):
        return render_template("detailed.html", table=[])

    # ---------------- AVAILABLE YEARS (TABLE) ----------------
    df_years = pd.read_excel(table_file_path)
    df_years.columns = (
        df_years.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    available_years = sorted(
        df_years["year"].dropna().astype(int).unique().tolist()
    )

    year = safe_int(request.form.get("year"))
    if year not in available_years:
        year = available_years[0]

    # ---------------- MAIN TABLE ----------------
    df = get_detailed_data(
        year=year,
        file_path=table_file_path,
        selected_columns=selected_columns,
        selected_months=selected_months
    )

    df = df.drop(
        columns=[c for c in ["monthly_growth", "monthly_cost_growth"] if c in df.columns],
        errors="ignore"
    )

    # ---------------- GRAPH BUILDER ----------------
    graph_mineral = request.form.get("graph_mineral") or mineral
    graph_columns = request.form.getlist("graph_columns")

    # fallback so dropdown is not empty initially
    if not graph_columns and selected_columns:
        graph_columns = selected_columns

    valid_graphs = get_valid_graphs(graph_columns)

    graph_file_path = f"Data/{graph_mineral}/{graph_mineral.lower()}_{trade.lower()}.xlsx"
    graph_available_years = []

    if os.path.exists(graph_file_path):
        df_g = pd.read_excel(graph_file_path)
        df_g.columns = (
            df_g.columns.astype(str)
            .str.strip()
            .str.lower()
            .str.replace(" ", "_")
        )
        graph_available_years = sorted(
            df_g["year"].dropna().astype(int).unique().tolist()
        )


    # ---------------- GROWTH ----------------
    growth_result = None
    growth_label = None

    growth_mineral = request.form.get("growth_mineral") or mineral
    growth_column = request.form.get("growth_column")
    growth_mode = request.form.get("growth_mode")

    start_month = request.form.get("start_month")
    end_month = request.form.get("end_month")

    start_year = safe_int(
        request.form.get("start_year_monthly")
        if growth_mode == "monthly"
        else request.form.get("start_year_yearly")
    )

    end_year = safe_int(
        request.form.get("end_year_monthly")
        if growth_mode == "monthly"
        else request.form.get("end_year_yearly")
    )

    growth_file_path = f"Data/{growth_mineral}/{growth_mineral.lower()}_{trade.lower()}.xlsx"

    if request.form.get("calculate_growth") == "1":

        if not growth_column:
            growth_label = "Please select a growth column"

        elif not os.path.exists(growth_file_path):
            growth_label = "No data file for selected growth mineral"

        else:
            df_all = pd.read_excel(growth_file_path)
            df_all.columns = (
                df_all.columns.astype(str)
                .str.strip()
                .str.lower()
                .str.replace(" ", "_")
            )

            if growth_column not in df_all.columns or not pd.api.types.is_numeric_dtype(df_all[growth_column]):
                growth_label = "Selected growth column is not numeric"

            elif growth_mode == "yearly":
                old_df = df_all[df_all["year"] == start_year]
                new_df = df_all[df_all["year"] == end_year]

                if old_df.empty or new_df.empty:
                    growth_label = "No data for selected year(s)"

                else:
                    old = old_df[growth_column].iloc[0]
                    new = new_df[growth_column].iloc[0]

                    if old == 0:
                        growth_label = "Start year value is zero"
                    else:
                        growth_result = round(((new - old) / old) * 100, 2)
                        growth_label = f"{start_year} → {end_year}"

            elif growth_mode == "monthly":
                old_df = df_all[
                    (df_all["year"] == start_year) &
                    (df_all["month"] == start_month)
                ]
                new_df = df_all[
                    (df_all["year"] == end_year) &
                    (df_all["month"] == end_month)
                ]

                if old_df.empty or new_df.empty:
                    growth_label = "No data for selected month/year"

                else:
                    old = old_df[growth_column].iloc[0]
                    new = new_df[growth_column].iloc[0]

                    if old == 0:
                        growth_label = "Start value is zero"
                    else:
                        growth_result = round(((new - old) / old) * 100, 2)
                        growth_label = f"{start_month} {start_year} → {end_month} {end_year}"

    return render_template(
        "detailed.html",
        mineral=mineral,
        trade=trade,
        year=year,
        table=df.to_dict("records"),
        selected_columns=selected_columns,
        selected_months=selected_months,
        available_years=available_years,

        # GRAPH
        graph_mineral=graph_mineral,
        graph_columns=graph_columns,
        graph_available_years=graph_available_years,
        valid_graphs=valid_graphs,

        # GROWTH
        growth_result=growth_result,
        growth_label=growth_label
    )


    

@app.route("/plot", methods=["POST"])
def plot():

    graph_mineral = request.form.get("graph_mineral")
    graph_year = safe_int(request.form.get("graph_year"))
    graph_months = request.form.getlist("graph_months")
    graph_columns = request.form.getlist("graph_columns")
    graph_types = request.form.getlist("graph_types")

    trade = request.form.get("trade", "Export")

    file_path = f"Data/{graph_mineral}/{graph_mineral.lower()}_{trade.lower()}.xlsx"

    if not os.path.exists(file_path):
        return "No data file found"

    # 1️⃣ LOAD DATA
    df = pd.read_excel(file_path)
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    # 2️⃣ KEEP ONLY NUMERIC GRAPH COLUMNS
    numeric_cols = [
        c for c in graph_columns
        if c in df.columns and pd.api.types.is_numeric_dtype(df[c])
    ]

    if not numeric_cols:
        return "Selected graph columns are not numeric"

    # 3️⃣ FILTER BY YEAR
    if graph_year:
        df = df[df["year"] == graph_year]

    # 4️⃣ NORMALIZE MONTH COLUMN
    MONTH_NORMALIZE = {
        "1": "Jan", "2": "Feb", "3": "Mar", "4": "Apr",
        "5": "May", "6": "Jun", "7": "Jul", "8": "Aug",
        "9": "Sep", "10": "Oct", "11": "Nov", "12": "Dec",
        "january": "Jan", "february": "Feb", "march": "Mar",
        "april": "Apr", "may": "May", "june": "Jun",
        "july": "Jul", "august": "Aug", "september": "Sep",
        "october": "Oct", "november": "Nov", "december": "Dec"
    }

    df["month"] = (
        df["month"]
        .astype(str)
        .str.strip()
        .str.lower()
        .map(MONTH_NORMALIZE)
    )

    df = df[df["month"].notna()]

    # 5️⃣ FILTER BY MONTHS
    if graph_months:
        df = df[df["month"].isin(graph_months)]

    # 6️⃣ ORDER MONTHS
    MONTH_ORDER = [
        "Jan","Feb","Mar","Apr","May","Jun",
        "Jul","Aug","Sep","Oct","Nov","Dec"
    ]

    df["month"] = pd.Categorical(
        df["month"],
        categories=MONTH_ORDER,
        ordered=True
    )
    df = df.sort_values("month")

    # 7️⃣ GENERATE GRAPHS
    from services.graph_service import plot_graph
    import matplotlib.pyplot as plt

    image_paths = []

    for g in graph_types:
        plt.clf()

        title = f"{graph_mineral} - {graph_year} ({g.replace('_',' ').title()})"
        plot_graph(df, g, numeric_cols, title)

        filename = f"{g}_{uuid.uuid4().hex}.png"
        path = os.path.join("static/plots", filename)
        plt.savefig(path, dpi=120, bbox_inches="tight")
        image_paths.append(path)

    return render_template(
        "graphs.html",
        image_paths=image_paths
    )



from services.ml_predict import predict_future


@app.route("/predict", methods=["GET", "POST"])
def predict():
    result = None
    error = None

    if request.method == "POST":
        try:
            mineral = request.form.get("mineral").lower()
            trade = request.form.get("trade").lower()
            metric = request.form.get("metric")
            year = int(request.form.get("year"))
            month = int(request.form.get("start_month"))   # ✅ ADD THIS
            months = int(request.form.get("months"))

            df = predict_future(
                mineral=mineral,
                trade=trade,
                metric=metric,
                start_year=year,
                start_month=month,      # ✅ PASS IT
                months_ahead=months
            )

            result = df.to_dict("records")

        except Exception as e:
            error = str(e)

    return render_template("predict.html", result=result, error=error)



if __name__ == "__main__":
    app.run(debug=True)
