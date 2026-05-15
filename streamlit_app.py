# Import python packages.
import streamlit as st
import requests

from snowflake.snowpark.functions import col

# Write directly to the app.
cnx = st.connection("snowflake")

st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")

st.write("Choose the fruits you want in your smoothie")

session = cnx.session()

name_on_order = st.text_input('Name on Smoothie:')

st.write('The name on the smoothie will be:', name_on_order)

my_dataframe = (
    session.table("smoothies.public.fruit_options")
    .select(col('FRUIT_NAME'))
)

fruit_rows = my_dataframe.collect()

fruit_list = [row["FRUIT_NAME"] for row in fruit_rows]

ingredients_list = st.multiselect(
    "Choose upto 5 ingredients",
    fruit_list,
    max_selections=5,
)

if ingredients_list:

    ingredients_string = ''

    for fruit_chosen in ingredients_list:

        ingredients_string += fruit_chosen + ' '

        st.subheader(fruit_chosen + ' Nutrition Information')

        smoothiefroot_response = requests.get(
            "https://fruityvice.com/api/fruit/" + fruit_chosen
        )

        st.dataframe(
            data=smoothiefroot_response.json(),
            use_container_width=True
        )

    my_insert_stmt = f"""
        insert into smoothies.public.orders
        (ingredients, name_on_order)
        values
        ('{ingredients_string}', '{name_on_order}')
    """

    time_to_insert = st.button('Submit Order')

    if time_to_insert:

        session.sql(my_insert_stmt).collect()

        st.success(
            f'Your Smoothie is ordered! {name_on_order}!',
            icon="✅"
        )
