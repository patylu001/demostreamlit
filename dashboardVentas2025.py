import streamlit as st
import pandas as pd
import plotly.express as px

# Function to load the data
@st.cache_data
def load_data(file_path):
    df = pd.read_excel(file_path)
    return df

# Function to create the top selling products bar chart
def plot_top_selling_products(df):
    product_sales = df.groupby('Product Name')['Sales'].sum().sort_values(ascending=False)
    top_5_products = product_sales.head(5)
    fig = px.bar(top_5_products, x=top_5_products.index, y=top_5_products.values,
                 labels={'x': 'Product Name', 'y': 'Sales'},
                 title='Top 5 Selling Products')
    fig.update_layout(xaxis={'categoryorder':'total descending'})
    return fig

# Function to create the top profitable products bar chart
def plot_top_profitable_products(df):
    product_profit = df.groupby('Product Name')['Profit'].sum().sort_values(ascending=False)
    top_5_profitable_products = product_profit.head(5)
    fig = px.bar(top_5_profitable_products, x=top_5_profitable_products.index, y=top_5_profitable_products.values,
                 labels={'x': 'Product Name', 'y': 'Profit'},
                 title='Top 5 Most Profitable Products')
    fig.update_layout(xaxis={'categoryorder':'total descending'})
    return fig

# Main Streamlit app
def main():
    st.title("Product Analysis Dashboard")

    file_path = "SalidaFinal.xlsx"
    df = load_data(file_path)

    st.write("## Data Preview")
    st.dataframe(df.head())

    st.write("## Top 5 Selling Products")
    sales_fig = plot_top_selling_products(df)
    st.plotly_chart(sales_fig)

    st.write("## Top 5 Most Profitable Products")
    profit_fig = plot_top_profitable_products(df)
    st.plotly_chart(profit_fig)

if __name__ == "__main__":
    main()
