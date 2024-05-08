"""
Name:       Tony Cristiani
CS230:      Section 004
Data:       Nuclear Explosions
URL:

Description: In this code I have made multiple maps and charts displaying information about nuclear detonations from the
past century. I use bar graphs to display the amount of detonations recorded by countries and based on the information
given. The code is set up so that the user can easily understand what is going on and what each chart or map represents.
I have created 3 bar charts one with a trend line 3 maps a pie chart, and a relplot.

"""
import streamlit as st
import pydeck as pdk
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_option('deprecation.showPyplotGlobalUse', False)


def home_page():
    st.title("Nuclear Detonation Visualization")
    st.write("Welcome to the Nuclear Detonation Visualization tool, an interactive web application designed to provide "
             "insights into nuclear detonations around the globe. This tool allows users to explore various aspects of "
             "nuclear tests, including their locations, frequencies, and the countries involved.")
    st.image("https://t3.ftcdn.net/jpg/05/50/55/78/360_F_550557805_B87SNs3Eo2LGsQV61VwnhDF9fSKCmpzU.jpg", width=700)
    st.subheader("Features:")  # not sure if covered in class sub headers
    st.write("- **General Map**: View a map highlighting all nuclear detonation sites.")
    st.write("- **Independent Map**: Dive deeper into each site with individual markers.")
    st.write("- **Heatmap**: Understand the density of nuclear tests.")
    st.write("- **Data Analytics**: Analyze the detonations including visualizations of number of detonations by "
             "country and the yield of the detonations")
    st.write("Navigate through the sidebar to explore different visualizations and data insights. Each section "
             "provides interactive controls to customize the view according to your needs.")


# [PY2], [PY3]
def read_data():
    path = "C:/Users/tcris/OneDrive - Bentley University/CS-230/Python Project/Final Project/"
    lat_shift = 0.2
    lon_shift = 0.2
    df = pd.read_csv(path + "nuclear_explosions.csv")

    # [DA1]
    df.rename(columns={"Location.Cordinates.Latitude": "lat", "Location.Cordinates.Longitude": "lon"}, inplace=True)

    df['lat'] += lat_shift
    df['lon'] += lon_shift
    return df, path


def general_nuke_map(data):
    df = data

    st.title("General Map of Nukes Detonated Around the World")

    view_state = pdk.ViewState(latitude=df["lat"].mean(),
                               longitude=df["lon"].mean(),
                               zoom=0.5,
                               pitch=0)

    layer = pdk.Layer(type='ScatterplotLayer',
                      data=df,
                      get_position='[lon, lat]',
                      get_radius=100000,
                      get_color=[255, 204, 0],
                      pickable=True)

    # [PY5] Used in all three maps
    tool_tip = {"html": "Bomb Name: <b>{Data.Name}</b><br> Location: <b>{WEAPON DEPLOYMENT LOCATION}</b><br> "
                        "Weapon from: <b>{WEAPON SOURCE COUNTRY}</b>",
                "style": {"backgroundColor": "black", "color": "yellow"}}

    gen_map = pdk.Deck(map_style='mapbox://styles/mapbox/satellite-streets-v12',
                       initial_view_state=view_state,
                       layers=[layer],
                       tooltip=tool_tip)

    st.pydeck_chart(gen_map)


def independent_nuke_map(data):
    df = data

    st.title("Independent Map of Nukes Detonated Around the World")

    view_state = pdk.ViewState(latitude=df["lat"].mean(),
                               longitude=df["lon"].mean(),
                               zoom=0.5,
                               pitch=0)

    layer = pdk.Layer(type='ScatterplotLayer',
                      data=df,
                      get_position='[lon, lat]',
                      get_radius=300,
                      get_color=[255, 0, 0],
                      pickable=True)

    tool_tip = {"html": "Bomb Name: <b>{Data.Name}</b><br> Location: <b>{WEAPON DEPLOYMENT LOCATION}</b><br> "
                        "Weapon from: <b>{WEAPON SOURCE COUNTRY}</b>",
                "style": {"backgroundColor": "black", "color": "yellow"}}

    ind_map = pdk.Deck(map_style='mapbox://styles/mapbox/satellite-streets-v12',
                       initial_view_state=view_state, layers=[layer],
                       tooltip=tool_tip)

    st.pydeck_chart(ind_map)


# Did not learn how to make heat maps
def heatmap(data):
    # [PY4], [DA8]
    # uses list comprehension and iterrows to only include data where both coordinates are given and the yield of the
    # explosive is bigger than 100 so that the heatmap is not to clustered by insignificant data.
    df = pd.DataFrame([row for index, row in data.iterrows()
                       if not pd.isnull(row['lat']) and
                       not pd.isnull(row['lon']) and
                       row['Data.Yeild.Upper'] > 100],
                      columns=data.columns)

    view_state = pdk.ViewState(latitude=df['lat'].mean(),
                               longitude=df['lon'].mean(),
                               zoom=1,
                               pitch=0)
    heatmap_layer = pdk.Layer("HeatmapLayer",
                              data=df,
                              get_position='[lon, lat]',
                              radius=100,
                              intensity=1,
                              threshold=0.5,
                              get_weight="1")

    heat_map = pdk.Deck(map_style='mapbox://styles/mapbox/dark-v9',
                        initial_view_state=view_state,
                        layers=[heatmap_layer])

    st.pydeck_chart(heat_map)


# [PY1] almost all my functions use a default parameter
def country_nuke_count(data, selected_countries, show_data=False):
    # [DA6] Using a pivot table to ensure that the selected countries are shown
    pivot_table = data[data['WEAPON SOURCE COUNTRY'].isin(selected_countries)].pivot_table(
        index='WEAPON SOURCE COUNTRY',
        values='Data.Name',
        aggfunc='count'
        # [DA2] Also used in other parts of my code
    ).rename(columns={'Data.Name': 'Detonations'}).sort_values(by='Detonations', ascending=False)

    # [DA7] Also used in other parts of my code
    pivot_table.reset_index(inplace=True)
    pivot_table.columns = ['Country', 'Detonations']

    # Did not learn fig or ax in class (subplot)
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor('grey')
    ax.set_facecolor('grey')
    ax.bar(pivot_table['Country'], pivot_table['Detonations'], color="yellow")
    ax.set_title('Number of Nukes Detonated by Country')
    ax.set_xlabel('Country')
    ax.set_ylabel('Number of Detonations')
    ax.set_xticks(range(len(pivot_table['Country'])))
    ax.set_xticklabels(pivot_table['Country'], rotation=45)

    st.pyplot(fig)

    if show_data:
        st.write(pivot_table)


def bar_chart_yearly_detonations(data, start_year, end_year, show_data=False):
    # [DA4] Also used in other parts of my code
    data = data[(data['Date.Year'] >= start_year) & (data['Date.Year'] <= end_year)]
    color_base = '#F5F50A'

    if data.index.name != 'Date.Year':
        data = data.set_index('Date.Year', drop=True)

    # [DA2] Also used in other parts of my code
    detonation_counts = data.index.value_counts().sort_index()

    # Did not learn fig or ax in class (subplot)
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor('grey')
    ax.set_facecolor('grey')
    ax.bar(detonation_counts.index, detonation_counts.values, color=color_base, label='Detonations')

    ax.plot(detonation_counts.index, detonation_counts.values, color='orange', marker='o', label='Trend Line')
    ax.set_xticks(detonation_counts.index)
    ax.set_xticklabels(detonation_counts.index, rotation=90)
    ax.set_title('Yearly Detonations')
    ax.set_xlabel('Year')
    ax.set_ylabel('Number of Detonations')
    plt.legend()
    st.pyplot(fig)

    if show_data:
        st.write(detonation_counts)


def stacked_bar_chart(data, start_year, end_year, selected_countries, show_data=False):
    # [DA2], [DA5] Also used in other parts of my code
    filtered_data = data[(data['Date.Year'] >= start_year) & (data['Date.Year'] <= end_year) &
                         (data['WEAPON SOURCE COUNTRY'].isin(selected_countries))]

    grouped_data = filtered_data.groupby(['Date.Year', 'WEAPON SOURCE COUNTRY']).size().unstack(fill_value=0)

    # Did not learn fig or ax in class (subplot)
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor('grey')
    ax.set_facecolor('grey')
    grouped_data.plot(kind='bar', stacked=True, ax=ax)
    ax.set_title('Yearly Detonations by Country')
    ax.set_xlabel('Year')
    ax.set_ylabel('Number of Detonations')
    ax.legend(title='Country')

    st.pyplot(fig)

    if show_data:
        st.write(grouped_data)


def pie_chart(data, selected_countries):

    if selected_countries:
        data = data[data['WEAPON SOURCE COUNTRY'].isin(selected_countries)]

    country_counts = data['WEAPON SOURCE COUNTRY'].value_counts()

    # Did not learn fig or ax in class (subplot)
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor('grey')
    ax.set_title('Proportion of Nukes by Country')

    ax.pie(country_counts, labels=country_counts.index, autopct='%1.1f%%')
    ax.legend(loc="upper right")

    st.pyplot(fig)


def nuke_yield_in_tnt(data, yield_min, yield_max, selected_countries, show_data):
    # [DA2], [DA5], [DA9] Also used in other parts of my code
    filtered_data = data[data['WEAPON SOURCE COUNTRY'].isin(selected_countries) & data['Data.Yeild.Upper'].notna() &
                         (data['Data.Yeild.Upper'] >= yield_min) & (data['Data.Yeild.Upper'] <= yield_max)]

    filtered_data = filtered_data.rename(columns={'WEAPON SOURCE COUNTRY': 'Country',
                                                  'Data.Yeild.Upper': 'Kilotons of TNT',
                                                  'Data.Type': 'Deployment Method'})

    chart_data = filtered_data[['Country', 'Kilotons of TNT', 'Deployment Method']]
    # [DA2] Also used in other parts of my code
    chart_data = chart_data.sort_values(by='Kilotons of TNT', ascending=False)

    # Did not learn sns or any of the things below this comment in this function
    plt.figure(figsize=(10, 6))
    sns.relplot(x="Country",
                y="Kilotons of TNT",
                hue="Deployment Method",
                size="Kilotons of TNT",
                sizes=(40, 400),
                alpha=.5,
                palette="muted",
                height=6,
                data=filtered_data)
    plt.title('Comparison of Nuclear Detonation Yields by Country')
    plt.ylabel('Yield Upper Estimate (kilotons of TNT)')
    plt.xlabel('Country')

    st.pyplot(plt.gcf())

    if show_data:
        st.write(chart_data)


def main():
    st.sidebar.title("Navigation")
    # did not learn how to set up page navigation
    page = st.sidebar.selectbox("Choose a page", ["Home Page", "General/Independent Map", "Heatmap",
                                                  "Country Detonation Count", "Yearly Detonations",
                                                  "Yearly Detonation Stacked by Country",
                                                  "Proportion of Detonations by Country", "Nuke Yield"])

    if page == "Home Page":
        home_page()
    elif page == "General/Independent Map":
        st.sidebar.subheader("Map Choice")
        general_map_description = "(Displays large areas for easier visualization of nuke locations)"
        independent_map_description = "(Displays more focused points to see each nuke individually)"
        map_type = st.sidebar.radio("Choose the map to display:", (f"General Map: {general_map_description}",
                                                                   f"Independent Map: {independent_map_description}"))
        if map_type == f'General Map: {general_map_description}':
            general_nuke_map(read_data()[0])
        elif map_type == f'Independent Map: {independent_map_description}':
            independent_nuke_map(read_data()[0])

    elif page == "Heatmap":
        st.title("Heatmap of Nuclear Detonations")
        heatmap(read_data()[0])

    elif page == "Country Detonation Count":
        st.sidebar.subheader("Filter Options")
        st.title("Number of Detonations by Country")
        # [DA2] Also used in other parts of my code
        countries = sorted(read_data()[0]['WEAPON SOURCE COUNTRY'].unique())
        selected_countries_nuke_count = st.sidebar.multiselect('Select a Country:', countries, default=countries)
        st.write(f"Selected Countries: {selected_countries_nuke_count}")
        show_data = st.sidebar.checkbox('Show number of detonations by country', value=False)
        country_nuke_count(read_data()[0], selected_countries_nuke_count, show_data)

    elif page == "Yearly Detonations":
        st.sidebar.subheader("Filter Options")
        st.title("Amount of Detonations by Year")
        start_year, end_year = st.sidebar.slider("Select year range.", 1945, 1998, [1945, 1998], 1)
        st.write(f"Displaying detonations from {start_year} to {end_year}")
        show_data = st.sidebar.checkbox('Show data for number of detonations by year', value=False)
        bar_chart_yearly_detonations(read_data()[0], start_year, end_year, show_data)

    elif page == "Yearly Detonation Stacked by Country":
        st.sidebar.subheader("Filter Options")
        st.title("Yearly Detonations by Country Stacked")
        # [DA2] Also used in other parts of my code
        years = sorted(read_data()[0]['Date.Year'].unique())
        # [DA3] Also used in other parts of my code
        stacked_min_year, stacked_max_year = (
            st.sidebar.slider("Select the year range.", min(years), max(years), [min(years), max(years)], 1))
        st.write(f"Displaying detonations from {stacked_min_year} to {stacked_max_year}")
        # [DA2] Also used in other parts of my code
        countries = sorted(read_data()[0]['WEAPON SOURCE COUNTRY'].unique())
        selected_countries_stacked = st.sidebar.multiselect('Select Countries:', countries, default=countries)
        st.write(f"Selected Countries: {selected_countries_stacked}")
        show_data = st.sidebar.checkbox('Show data for values of the chart', value=False)
        stacked_bar_chart(read_data()[0], stacked_min_year, stacked_max_year, selected_countries_stacked, show_data)

    elif page == "Proportion of Detonations by Country":
        st.sidebar.subheader("Filter Options")
        st.title("Proportion of Detonations by Country")
        # [DA2] Also used in other parts of my code
        countries = sorted(read_data()[0]['WEAPON SOURCE COUNTRY'].unique())
        selected_countries_pie = st.sidebar.multiselect('Select Countries for pie chart:', countries, default=countries)
        st.write(f"Selected Countries: {selected_countries_pie}")
        pie_chart(read_data()[0], selected_countries_pie)

    elif page == "Nuke Yield":
        st.sidebar.subheader("Yield Filter Options")
        st.title("Nuke Yield in Terms of Kilotons of TNT")
        # [DA2] Also used in other parts of my code
        countries = sorted(read_data()[0]['WEAPON SOURCE COUNTRY'].unique())
        selected_countries_yield = st.sidebar.multiselect('Select Countries:', countries, default=countries)
        yield_min, yield_max = st.sidebar.slider("Select magnitude range.", 0, 50000, [0, 50000], 1)
        st.write(f"Selected countries: {selected_countries_yield}")
        st.write(f"Displaying magnitude sizes from {yield_min} to {yield_max}")
        show_data = st.sidebar.checkbox('Show data for Nuke Yield', value=False)
        nuke_yield_in_tnt(read_data()[0], yield_min, yield_max, selected_countries_yield, show_data)


main()
