import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import folium
import requests
from io import StringIO

st.header("This is the app for Becks SE350 lab")
st.write("this is some text.")

uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()

    # To convert to a string based IO:
    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))

    # To read file as string:
    string_data = stringio.read()

# importing the raw csv file from github
url = "https://raw.githubusercontent.com/Beck-MN/SE_350-Streamlit-App/main/museum_data.csv"

# cleaning out the uneeded columns
st.header("Museum data")
keep = [
    "Museum Name",
    "Museum Type",
    "City (Administrative Location)",
    "State (Administrative Location)",
    "Income",
    "Revenue",
    "Longitude",
    "Latitude",
]
response = requests.get(url)
df = pd.read_csv(StringIO(response.text), usecols=keep)
df = st.data_editor(df, num_rows="dynamic")

# total number of museums
total = len(df)
st.header("Total number of museums: ")
st.write(f"{total}\n")

# seperate by museum type
st.header("Average income for museums (by type)")
museum_type = df.groupby("Museum Type")
# find mean of income for each and display
st.write(museum_type["Income"].mean())

# pie chart for museum types
museum_type_count = df["Museum Type"].value_counts().reset_index()
museum_type_count.columns = ["Museum Type", "Count"]

st.header("Distribution of Museums by type")
st.dataframe(museum_type_count)

fig = px.pie(
    museum_type_count,
    values="Count",
    names="Museum Type",
    title="Distribution of museums by type",
    color_discrete_sequence=px.colors.sequential.RdBu,
    hover_data=museum_type_count.columns,
)
st.plotly_chart(fig, use_container_width=True)

# income vs revenue histograms
hist1 = px.histogram(df, x="Museum Name", y="Income")
hist2 = px.histogram(df, x="Museum Name", y="Revenue")

st.header("Histogram of museum income")
st.plotly_chart(hist1, use_container_width=True)
st.header("Histogram of museum revenue")
st.plotly_chart(hist2, use_container_width=True)

# map of museum locations
st.header("Map of Museums")
df_new = df.dropna(subset=["Latitude", "Longitude"])
map = folium.Map(location=[44.9778, -93.2650], zoom_start=10)
# small list of what types will be whcih color
color_dict = {
    "ARBORETUM, BOTANICAL GARDEN, OR NATURE CENTER": "blue",
    "ART MUSEUM": "red",
    "CHILDREN'S MUSEUM": "green",
    "GENERAL MUSEUM": "yellow",
    "HISTORIC PRESERVATION": "orange",
    "HISTORY MUSEUM": "purple",
    "NATURAL HISTORY MUSEUM": "black",
    "SCIENCE & TECHNOLOGY MUSEUM OR PLANETARIUM": "pink",
    "ZOO, AQUARIUM, OR WILDLIFE CONSERVATION": "white",
}

# check every row and use the value in log and lat to place on map
for index, row in df_new.iterrows():
    folium.Marker(
        location=[row["Latitude"], row["Longitude"]],
        popup=f"{row['Museum Name']} - {row['Museum Type']}",
        # use the previoulsy defined list to assing color
        icon=folium.Icon(
            color=color_dict.get(row["Museum Type"], "gray")
        ),  # Default to gray if type is not found
    ).add_to(map)

map.save("museum_map.html")
HtmlFile = open("museum_map.html", "r", encoding="utf-8")
source_code = HtmlFile.read()
components.html(source_code, height=600)
