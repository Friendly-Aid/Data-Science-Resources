import streamlit as st
import pandas as pd
import numpy as np

# Sets the page to wide layout
st.set_page_config(layout='wide')

st.title("My Streamlit App")
st.header("Metrics",divider="blue")
col1,col2,col3 = st.columns(3)
# Generate random data
data_size=100
data = pd.DataFrame({
    'Temperature': np.random.randint(10, 46, data_size),  # Temperature in the range from -51 to 46
    'Humidity': np.random.randint(63, 91, data_size),      # Humidity from 0 to 100
    'Rain': np.random.randint(10, 51, data_size)           # Rain in the range from 0 to 100
})

average_rain = data['Rain'].mean()
average_temp = data['Temperature'].mean()
average_humidity = data['Humidity'].mean()
rain_percent=((data['Rain'][data_size-1]-average_rain)/average_rain)*100
temp_percent=((average_temp-data['Temperature'][data_size-1])/average_temp)*100
humidity_percent=((data['Humidity'][data_size-1]-average_humidity)/average_humidity)*100
st.header(f"rain: {average_rain}, temp: {average_temp}, humidity: {average_humidity}")
col1.metric("rain",data["Rain"][data_size-1],f"{rain_percent:.2f}%")
col2.metric("temperature",data["Temperature"][data_size-1],f"{temp_percent:.2f}%")
col3.metric("humidity",data["Humidity"][data_size-1],f"{humidity_percent:.2f}%")
st.subheader("Line Charts",divider="gray")
st.line_chart(data)
