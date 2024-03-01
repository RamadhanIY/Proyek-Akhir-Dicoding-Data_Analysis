import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

# CSS
css_style = """
<style>
/* Atur font untuk judul */
.judul {
    font-family: Arial, sans-serif;
    font-size: 24px;
    font-weight: bold;
    color: #333333; /* Warna teks */
}

/* Atur font untuk teks */
.teks {
    font-family: 'Courier New', monospace;
    font-size: 16px;
    color: #333333; /* Warna teks */
}
</style>
"""


# Formatting Texts
def capitalize_words(string):
    words = string.split("_")

    capitalized_words = [word.capitalize() for word in words]

    capitalized_string = " ".join(capitalized_words)

    return capitalized_string


def create_mean_review_items_df(df):
    mean_review_items_df = (
        df.groupby(by="product_category_name_english")
        .review_score.mean()
        .sort_values(ascending=False)
    )

    review_summary = df.groupby("product_category_name_english").agg(
        {"review_score": ["count", "mean"]}
    )

    highest_rated_category = review_summary["review_score"]["mean"].idxmax()

    # Temukan jumlah review untuk kategori tersebut
    total_reviews = review_summary.loc[
        highest_rated_category, ("review_score", "count")
    ]

    # Temukan rata-rata rating untuk kategori tersebut
    average_rating = review_summary.loc[
        highest_rated_category, ("review_score", "mean")
    ]

    return highest_rated_category, total_reviews, average_rating, mean_review_items_df


def create_by_customer_state_df(df):
    by_customer_state_df = pd.DataFrame(
        df.groupby(by="customer_state")
        .customer_id.nunique()
        .sort_values(ascending=False)
    )
    by_customer_state_df.rename(
        columns={
            "customer_id": "customer_count",
        },
        inplace=True,
    )

    states = {
        "SP": "São Paulo",
        "MG": "Minas Gerais",
        "RJ": "Rio de Janeiro",
        "PR": "Paraná",
        "RS": "Rio Grande do Sul",
        "SC": "Santa Catarina",
        "BA": "Bahia",
        "GO": "Goiás",
        "ES": "Espírito Santo",
        "DF": "Distrito Federal",
        "PE": "Pernambuco",
        "PA": "Pará",
        "CE": "Ceará",
        "MA": "Maranhão",
        "MS": "Mato Grosso do Sul",
        "MT": "Mato Grosso",
        "PB": "Paraíba",
        "RN": "Rio Grande do Norte",
        "SE": "Sergipe",
        "RO": "Rondônia",
        "TO": "Tocantins",
        "PI": "Piauí",
        "AL": "Alagoas",
        "AC": "Acre",
        "AM": "Amazonas",
    }

    by_customer_state_df.reset_index(inplace=True)
    by_customer_state_df["customer_state"] = by_customer_state_df["customer_state"].map(
        states
    )

    return by_customer_state_df


def create_rfm(df):
    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
    rfm_df = (
        df.groupby("customer_id")["order_purchase_timestamp"]
        .max()
        .sort_values(ascending=False)
        .reset_index()
    )

    max_date = rfm_df["order_purchase_timestamp"].max()
    rfm_df["recency"] = (max_date - rfm_df["order_purchase_timestamp"]).dt.days

    return rfm_df[["customer_id", "recency"]]


# Gathering Dataset
merged_all = pd.read_csv("Dataset/merged_all.csv")

merged_all["order_purchase_timestamp"] = pd.to_datetime(
    merged_all["order_purchase_timestamp"]
)

# Filtering
min_date = merged_all["order_purchase_timestamp"].min()
max_date = merged_all["order_purchase_timestamp"].max()


with st.sidebar:
    st.image(
        "https://github.com/RamadhanIY/Proyek-Akhir-Dicoding-Data_Analysis/blob/main/Logo_Fashion_2.png?raw=true"
    )
    start_date, end_date = st.date_input(
        label="Time Range",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date],
    )


main_df = merged_all[
    (merged_all["order_purchase_timestamp"] >= str(start_date))
    & (merged_all["order_purchase_timestamp"] <= str(end_date))
]

by_customer_state = create_by_customer_state_df(main_df)
highest_rated_category, total_reviews, average_rating, mean_review_items_df = (
    create_mean_review_items_df(main_df)
)
rfm = create_rfm(main_df)


# Plot

st.header("Fashion Products Dashboard 👜")


st.subheader("Average Review Ratings")
col1, col2 = st.columns([3, 1])

with col1:

    fig, ax = plt.subplots(figsize=(35, 15))
    colors = [
        "#7469B6",
        "#FFE6E6",
        "#FFE6E6",
        "#FFE6E6",
        "#FFE6E6",
        "#FFE6E6",
        "#FFE6E6",
    ]

    sns.barplot(
        x="review_score",
        y="product_category_name_english",
        data=pd.DataFrame(mean_review_items_df.sort_values(ascending=False)),
        palette=colors,
    )
    ax.set_ylabel("Product Category Name")
    ax.set_xlabel("Review Score")
    ax.set_title("Best Review Score on Average", loc="center", fontsize=50)

    ax.tick_params(axis="x", labelsize=30)
    ax.tick_params(axis="y", labelsize=35)

    st.pyplot(fig)

with col2:
    st.markdown(
        '<p class="judul">Reviews</p>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<p class="teks">Best Seller Categories: <b>{capitalize_words(highest_rated_category)}</b></p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<p class="teks">Rata-rata rating: <b>{average_rating:.2f}/5</b></p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<p class="teks">Jumlah pembelian: <b>{total_reviews}</b></p>',
        unsafe_allow_html=True,
    )

st.subheader("Geospatial Analysis Based on the Most Orders")
fig, ax = plt.subplots(figsize=(20, 10))
colors = [
    "#7469B6",
    "#FFE6E6",
    "#FFE6E6",
    "#FFE6E6",
    "#FFE6E6",
    "#FFE6E6",
    "#FFE6E6",
    "#FFE6E6",
    "#FFE6E6",
    "#FFE6E6",
]

sns.barplot(
    x="customer_count",
    y="customer_state",
    data=by_customer_state.sort_values(by="customer_count", ascending=False).head(10),
    palette=colors,
    ax=ax,
)
ax.set_title("Number of Customer by States", loc="center", fontsize=50)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis="y", labelsize=30)
ax.tick_params(axis="x", labelsize=35)
st.pyplot(fig)

st.subheader("Recency Analysis")

fig = plt.figure(figsize=(10, 6))
plt.hist(rfm["recency"], bins=30, color="pink", edgecolor="black")
plt.title("Distribusi Recency Pelanggan")
plt.xlabel("Recency (Hari)")
plt.ylabel("Jumlah Pelanggan")
plt.grid(True)
st.pyplot(fig)
