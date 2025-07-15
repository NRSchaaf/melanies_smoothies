
# Import python packages
import streamlit as st
import requests
from snowflake.snowpark.functions import col

# App title and instructions
st.title("Customize Your SMoothie :cup_with_straw:")
st.write("**Choose the fruits you want in your custom Smoothie!**")

# Input for name on order
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Get fruit options including SEARCH_ON
fruit_df = session.table("smoothies.public.fruit_options").select(
    col('FRUIT_NAME'), col('SEARCH_ON')
).to_pandas()

fruit_list = fruit_df['FRUIT_NAME'].tolist()

# Multiselect for ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_list,
    max_selections=5
)

# Handle order submission
if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)
    st.write("Ingredients selected:", ingredients_string)

    for fruit_chosen in ingredients_list:
        search_value = fruit_df.loc[fruit_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].values[0]

        st.subheader(f"{fruit_chosen} Nutrition Information")

        try:
            response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_value.lower()}", timeout=5)
            if response.status_code == 200:
                st.dataframe(data=response.json(), use_container_width=True)
            else:
                st.warning(f"No data found for {fruit_chosen} (status code {response.status_code})")
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching data for {fruit_chosen}: {e}")

    # Prepare and show SQL insert statement
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """
    st.write(my_insert_stmt)

    # Submit button
    if st.button('Submit Order'):
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
