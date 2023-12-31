from urllib.error import URLError

import pandas
import requests
import snowflake.connector
import streamlit


def get_fruityvoice_data(fruit_choice):
    fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{fruit_choice}")
    return pandas.json_normalize(fruityvice_response.json())


def get_fruit_load_list(my_cnx):
    with  my_cnx.cursor() as my_cur:
        my_cur.execute("select * from fruit_load_list")
        return my_cur.fetchall()


def add_fruit_to_list(my_cnx, fruit_to_add):
    with  my_cnx.cursor() as my_cur:
        streamlit.text(f"Thanks for adding {fruit_to_add}")
        my_cur.execute("insert into fruit_load_list values(%s)", (fruit_to_add,))
        return f"Thanks for adding {fruit_to_add}"


streamlit.title("My Parents' New Healthy Diner")

streamlit.header("Breakfast Favourites")
streamlit.text("🥣 Omega 3 & Blueberry Oatmeal")
streamlit.text("🥗 Kale, Spinach & Rocket Smoothie")
streamlit.text("🐔 Hard-Boiled Free-Range Egg")
streamlit.text("🥑🍞 Avocado Toast")

streamlit.header("🍌🥭 Build Your Own Fruit Smoothie 🥝🍇")

my_fruit_list = pandas.read_csv("https://uni-lab-files.s3.us-west-2.amazonaws.com/dabw/fruit_macros.txt")
my_fruit_list = my_fruit_list.set_index("Fruit")

# Let"s put a pick list here so they can pick the fruit they want to include 
fruits_selected = streamlit.multiselect("Pick some fruits:", list(my_fruit_list.index), default=["Avocado", "Strawberries"])

fruits_to_show = my_fruit_list.loc[fruits_selected]

# Display the table on the page.
streamlit.dataframe(fruits_to_show)

streamlit.header("Fruityvice Fruit Advice!")

try:
    fruit_choice = streamlit.text_input('What fruit would you like information about?')
    if not fruit_choice:
        streamlit.error("Please select a fruit to get information")
    else:
        fruityvice_normalized = get_fruityvoice_data(fruit_choice=fruit_choice)
        streamlit.dataframe(fruityvice_normalized)
except URLError as e:
    streamlit.error(e)


if streamlit.button("Get Fruit Load List"):
    my_cnx = snowflake.connector.connect(**streamlit.secrets["snowflake"])
    my_data_rows = get_fruit_load_list(my_cnx=my_cnx)
    streamlit.dataframe(my_data_rows)
    my_cnx.close()


fruit_to_add = streamlit.text_input('What fruit would you like to add?')

if streamlit.button("Add a fruit to the list"):
    my_cnx = snowflake.connector.connect(**streamlit.secrets["snowflake"])
    result = add_fruit_to_list(my_cnx=my_cnx, fruit_to_add=fruit_to_add)
    streamlit.text(result)
    my_cnx.close()
