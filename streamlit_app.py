# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(f"Customize Your SMoothie :cup_with_straw:") #{st.__version__}
st.write(
  """**Choose the fruits you want in your custom Smoothie!**"""
)

name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Get fruit options
fruit_df = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME')).to_pandas()
fruit_list = fruit_df['FRUIT_NAME'].tolist()

# Multiselect for ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:'
    , fruit_list
    , max_selections=5
    )

# Handle order submission
if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

    st.write(ingredients_string)

    my_insert_stmt = f""" insert into smoothies.public.orders(ingredients, name_on_order)
            values ('{ingredients_string.strip()}', '{name_on_order}')"""

    st.write(my_insert_stmt)
    #st.stop()
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
