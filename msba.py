import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import seaborn as sns

# Load the dataset
file_path = 'https://linked.aub.edu.lb/pkgcube/data/be199751997f972c06a17d1d33c67cd7_20240905_224346.csv'
data = pd.read_csv(file_path)

# Extract governate from the refArea column
data['Governate'] = data['refArea'].apply(lambda url: url.split('/page/')[-1] if '/page/' in url else url.split('/resource/')[-1])

# Clean and filter relevant data
data['Town'] = data['Town'].fillna('Unknown Town')
data_cleaned = data[['Governate', 'PercentageofEducationlevelofresidents-illeterate',
                     'PercentageofEducationlevelofresidents-university',
                     'PercentageofEducationlevelofresidents-secondary',
                     'PercentageofEducationlevelofresidents-vocational',
                     'PercentageofEducationlevelofresidents-elementary']].dropna()

# Aggregate data by governate (mean of education levels)
data_by_governate = data_cleaned.groupby('Governate').mean(numeric_only=True).reset_index()

# Define the coordinates for each governate
coordinates = [
    {"name": "Aley_District", "latitude": 33.7750374995954, "longitude": 35.6062806},
    {"name": "Baabda_District", "latitude": 33.836497599596946, "longitude": 35.5912851},
    {"name": "Batroun_District", "latitude": 34.23332869961018, "longitude": 35.782262},
    {"name": "Bsharri_District", "latitude": 34.244631499610634, "longitude": 36.0380509},
    {"name": "Mount_Lebanon_Governorate", "latitude": 33.65686039959283, "longitude": 35.57410829999999},
    {"name": "Baalbek-Hermel_Governorate", "latitude": 34.39054479961699, "longitude": 36.3326578},
    {"name": "Byblos_District", "latitude": 34.139789599606544, "longitude": 35.799440499999996},
    {"name": "South_Governorate", "latitude": 33.52318379959052, "longitude": 35.6000068},
    {"name": "Keserwan_District", "latitude": 34.01476999960219, "longitude": 35.763974399999995},
    {"name": "North_Governorate", "latitude": 34.33810129961462, "longitude": 35.80583519999999},
    {"name": "Matn_District", "latitude": 33.92194799959932, "longitude": 35.6996504},
    {"name": "Miniyeh-Danniyeh_District", "latitude": 34.38345229961666, "longitude": 36.06199209999999},
    {"name": "Western_Beqaa_District", "latitude": 33.528513399590594, "longitude": 35.89803179999999},
    {"name": "Tyre_District", "latitude": 33.226737699587694, "longitude": 35.2728742},
    {"name": "Zahlé_District", "latitude": 33.84388039959714, "longitude": 35.9713729},
    {"name": "Zgharta_District", "latitude": 34.36265839961572, "longitude": 35.908301099999996},
    {"name": "Hasbaya_District", "latitude": 33.377383599588725, "longitude": 35.7321799},
    {"name": "Nabatieh_Governorate", "latitude": 33.401535899588964, "longitude": 35.4566784},
    {"name": "Sidon_District", "latitude": 33.46253109958969, "longitude": 35.3436941},
]

# Create a mapping from name to coordinates
coordinates_dict = {coord["name"]: coord for coord in coordinates}

# Assign the correct latitude and longitude from the coordinates
data_by_governate['lat'] = data_by_governate['Governate'].map(lambda x: coordinates_dict.get(x, {}).get('latitude', None))
data_by_governate['lon'] = data_by_governate['Governate'].map(lambda x: coordinates_dict.get(x, {}).get('longitude', None))

# Mapping dictionary for user-friendly education level names to actual column names in the data
education_columns = {
    'Illiterate': 'PercentageofEducationlevelofresidents-illeterate',
    'University': 'PercentageofEducationlevelofresidents-university',
    'Secondary': 'PercentageofEducationlevelofresidents-secondary',
    'Vocational': 'PercentageofEducationlevelofresidents-vocational',
    'Elementary': 'PercentageofEducationlevelofresidents-elementary'
}

# Streamlit app
def main():
    st.title("Lebanon Educational Levels Overview by Governate")

    # Checkbox to show/hide dataframe
    if st.checkbox('Show raw data'):
        st.dataframe(data_by_governate)

    # Sidebar for user interaction
    education_level = st.sidebar.selectbox(
        "Select Education Level to Visualize on Map",
        list(education_columns.keys())
    )

    # Get the correct column name from the dictionary
    selected_column = education_columns[education_level]

    # Map Visualization (with Folium)
    st.subheader("Map of Educational Levels by Governate")
    m = folium.Map(location=[33.8547, 35.8623], zoom_start=7)

    marker_cluster = MarkerCluster().add_to(m)
    for i, row in data_by_governate.iterrows():
        if pd.notnull(row['lat']) and pd.notnull(row['lon']):
            folium.Marker(
                location=[row['lat'], row['lon']],
                popup=f"Governate: {row['Governate']}<br>{education_level} Level: {row[selected_column]:.2f}%",
            ).add_to(marker_cluster)

    # Display the map using st_folium
    st_folium(m)

    # Set a reasonable y-axis limit
    y_axis_limit = 50  # Adjust based on what looks good for your data

    # Bar chart for selected education level
    st.subheader(f"Comparison of {education_level} Education Levels by Governate")
    fig, ax = plt.subplots()
    governates = data_by_governate['Governate']
    education_values = data_by_governate[selected_column]
    ax.bar(governates, education_values)
    ax.set_xlabel('Governate')
    ax.set_ylabel(f'{education_level} (%)')
    ax.set_title(f'{education_level} Levels in Different Governates')
    ax.set_ylim([0, y_axis_limit])  # Set y-axis limit
    plt.xticks(rotation=90)
    st.pyplot(fig)

    # Scatter plot for interaction
    st.subheader("Interactive Scatter Plot of Education Levels")

    # Dropdown for user to select x and y axis for the scatter plot
    x_axis = st.selectbox("Select X-axis", list(education_columns.keys()), index=0)
    y_axis = st.selectbox("Select Y-axis", list(education_columns.keys()), index=1)

    # Create scatter plot using the selected x and y axes
    fig, ax = plt.subplots()
    sns.scatterplot(
        data=data_by_governate,
        x=education_columns[x_axis],
        y=education_columns[y_axis],
        hue='Governate',
        ax=ax
    )
    
    ax.legend().remove()
    ax.set_xlabel(f'{x_axis} (%)')
    ax.set_ylabel(f'{y_axis} (%)')
    ax.set_title(f'Scatter Plot: {x_axis} vs {y_axis}')
    st.pyplot(fig)

if __name__ == "__main__":
    main()
