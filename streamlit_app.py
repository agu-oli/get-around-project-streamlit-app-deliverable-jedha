import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import openpyxl
import plotly.express as px
import boto3

### Config
st.set_page_config(
    page_title="My_streamlit_projet",
    #page_icon="💸 ",
    layout="wide"
)

data_path = ('https://projet-deploiement-jedha.s3.eu-west-3.amazonaws.com/dataset_streamlit_app.xlsx')


### App
st.title("Get around case study")

st.markdown("""
GetAround is a car rental facility.

Since some drivers are late for checkout, which may cause friction with the following planned rental, a minimum delay between rentals has been implemented.

We will provide data insights to help the product manager decide on:
- The duration of the minimum delay
- The scope: to which types of cars this feature should be implemented?

The following questions will be addressed in this analysis:
- Drivers on time vs drivers late for check-out. How does it impact the next driver?
- What share of our owners' revenue would potentially be affected by the feature?
- How many problematic cases could be solved with this feature?
    - Check-in delay analysis
    - Analysis of problematic cases based on time delta:
        - All types of cars
        - Connect check-in cars vs. mobile check-in cars
""")



                              
@st.cache_data
def load_data():
    df = pd.read_excel(data_path)
    #df = pd.read_csv(DATA_URL)

    return df


data_load_state = st.text('Loading data...')
df = load_data()
data_load_state.text("") # change text from "Loading data..." to "" once the the load_data function has run

## Run the below code if the check is checked ✅
if st.checkbox('Show raw data'):
    st.subheader('Raw data used for this analysis')
    st.write(df)

st.subheader("Drivers on time vs drivers late for check-out")


# Calculate the percentage of drivers who returned the car on time or before the scheduled time
drivers_on_time = 100 * (df['delay_at_checkout_in_minutes'] <= 0).sum() / df.shape[0]
st.write("Percentage of drivers who returned their car on time or before the scheduled time:")
st.write(f"{drivers_on_time:.2f}%")

# Calculate the number of drivers who were late for check-out
drivers_late = (df['delay_at_checkout_in_minutes'] > 0).sum()
#st.subheader("Number of drivers late for check-out:")
#st.write(drivers_late)

percentage_drivers_late = 100 * (df['delay_at_checkout_in_minutes'] > 0).sum() / df.shape[0]
st.write("Percentage of drivers late for check-out:")
st.write(f"{percentage_drivers_late:.2f}%")


## Simple bar chart
# Data for the bar chart
labels = ['Drivers Late', 'Drivers On Time']
values = [percentage_drivers_late, drivers_on_time]

# Create the bar chart
fig = go.Figure(
    go.Bar(
        x=labels, 
        y=values,
        marker_color=['skyblue', 'lightcoral'],  # Colors for the bars
        text=[f'{val:.2f}%' for val in values],  # Add percentage text to the bars
        textposition='auto'  # Position text automatically
    )
)

# Show the figure
fig.show()

# Customize the layout
fig.update_layout(
    title='Percentage of Rentals Concerned and Drivers Status',
    yaxis_title='Percentage (%)',
    yaxis_range=[0, 100]  # Set y-axis range from 0 to 100
)

# Display the chart in Streamlit
st.plotly_chart(fig)


# Display stats for drivers on time and late
#st.subheader("First summary")
#st.write(f"32.5% of drivers returned their car on time or before the scheduled time.")
#st.write(f"44% of drivers are late for check-out.")

# Display additional information with markdown for formatting
st.subheader("Impact on Next Driver")
st.markdown("""
There are more drivers who are late for check-out than drivers on time:

- **32.5%** of drivers returned their car on time or before the scheduled time.
- **44%** of drivers are late for check-out""")

st.markdown("""
When this happens, the cars are late for the next check-in. Here’s a deeper look into the delays:
- The minimum waiting time was **30 minutes**.
- The worst-case scenario was **720 minutes**.
- **75%** of the clients waited up to **600 minutes**.
- **50%** of them waited up to **240 minutes**.
- On average, clients in this group waited **329 minutes**, with a standard deviation of **244 minutes**.
- Visualisations below:

the dataset doesn't show any data for time differences between two rentals that exceed **12 hours**.
""")
            
st.write("Time Delta between Rentals Chart")

# Histogram of the 'time_delta_with_previous_rental_in_minutes' column

df_late_checkin = df[df['time_delta_with_previous_rental_in_minutes'] > 0]

# Streamlit app title
st.write("Quartile Visualization of Time Delta Between Rentals")

# Box plot of 'time_delta_with_previous_rental_in_minutes' with updated layout
fig = px.box(df_late_checkin, y="time_delta_with_previous_rental_in_minutes", title="Box Plot: Time Delta Between Rentals",
             color_discrete_sequence=["#636EFA"])  # Adjust the color of the box plot (blue by default)

# Update layout to use a white background
fig.update_layout(
    plot_bgcolor="white",   # Set plot background to white
    paper_bgcolor="white",  # Set overall background to white
    font_color="black",     # Set font color to black for contrast
    title_x=0.5             # Center the title
)

# Display the box plot in Streamlit
st.plotly_chart(fig)

# Optional: Display basic statistics
st.write(df_late_checkin["time_delta_with_previous_rental_in_minutes"].describe())

st.subheader('Which is the share of the owner’s revenue that would potentially be affected by this new feature?')

# Calculations
num_rentals_concerned = df.previous_ended_rental_id.notnull().sum()
percentage_rentals_affected = 100 * num_rentals_concerned / df.shape[0]
total_rentals = df.shape[0]

# Display percentage in Streamlit
st.write(f"Total Rentals: {total_rentals}")
st.write(f"Rentals Affected: {num_rentals_concerned}")
st.write(f"Percentage of Rentals Affected: {percentage_rentals_affected:.2f}%")


# Optionally, display a gauge chart for percentage visualization
gauge_fig = px.pie(
    names=["Affected Rentals", "Unaffected Rentals"],
    values=[percentage_rentals_affected, 100 - percentage_rentals_affected],
    title="Percentage of Rentals Affected",
    hole=0.7  # Makes the pie chart a donut (gauge-like)
)

# Update gauge layout
gauge_fig.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white",
    font_color="black",
    title_x=0.5
)

# Display the gauge chart in Streamlit
st.plotly_chart(gauge_fig)

#st.markdown("""
#This number includes: all the rentals that were preceded by another rental within 12 hours""")


# Display results
st.write(f"Such a new feature would concern {num_rentals_concerned} of rentals, which is the total number of car rentals that were preceded by another rental within 12 hours.")

st.write(f"This means this feature would have an impact on {percentage_rentals_affected:.2f}% of the owner's share.")

st.markdown("""
Different thresholds can be applied to define the minimum time gap between two rentals of the same car.

Additionally, this feature can be applied to two different types of cars in our data:
            
* **Mobile cars**: Cars where the rental agreement is signed on the owner's smartphone.
* **Connect cars**: Cars equipped with Connect technology, allowing the driver to unlock the car using their smartphone.
""")


st.subheader(" How many problematic cases will this feature solve depending on the chosen threshold and scope?")

st.write('Problematic are those where the delay in the checkout also coincides with a delay in the planned of the following rental.')

# Calculate the number of problematic cases
prob_cases = ((df['time_delta_with_previous_rental_in_minutes'] > 0) & (df['delay_at_checkout_in_minutes'] > 0)).sum()

# Calculate the percentage of problematic cases over the total rentals
percentage_prob_cases = (100 * prob_cases) / df.shape[0]

non_prob_cases = df.shape[0] - prob_cases
percentage_non_prob_cases = 100 - percentage_prob_cases

# Create the donut-like pie chart (gauge style)
gauge_fig = px.pie(
    names=["Problematic Cases", "Non-Problematic Cases"],
    values=[percentage_prob_cases, percentage_non_prob_cases],
    title="Percentage of Problematic Cases",
    hole=0.7  # Makes it a donut (gauge-like)
)

# Update the layout for white background and better color contrast
gauge_fig.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white",
    font_color="black",
    title_x=0.5  # Centers the title
)

# Display the gauge chart in Streamlit
st.plotly_chart(gauge_fig)


# Display the information in Streamlit
st.subheader("Problematic Cases Resolved by the Feature")

st.write(f"It would resolve {prob_cases} problematic cases.")
st.write(f"This means {percentage_prob_cases:.2f}% of cases over the total number of rentals.")


st.subheader('Check-in Delay Analysis')
st.subheader("Scope and threshold analysis")

df_mobile = df[df['checkin_type']=='mobile']
df_connect = df[df['checkin_type']=='connect']
# Compute the number of rows where the time delta is between 0 and 30 minutes
num_cases_within_30_minutes_connect = ((df_connect['time_delta_with_previous_rental_in_minutes'] > 0) & 
                               (df_connect['time_delta_with_previous_rental_in_minutes'] <= 30) & 
                               (df_connect['delay_at_checkout_in_minutes'] > 0)).sum()

# Calculate the percentage
percentage_within_30_minutes_connect = 100 * num_cases_within_30_minutes_connect / prob_cases
# Display the result
print(f"- Percentage of problematic connect cases within 30 minutes: {percentage_within_30_minutes_connect:.2f}%")

# Calculate the percentage of cases within 30 minutes over the total number of rentals
percentage_within_30_minutes_over_total_connect = 100 * num_cases_within_30_minutes_connect / df_connect.shape[0]
# Display the result
print(f"- Percentage of problematic connect cases within 30 minutes over the total of rentals: {percentage_within_30_minutes_over_total_connect:.2f}%")

# Compute the number of rows where the time delta is between 0 and 60 minutes
num_cases_within_60_minutes_connect = ((df_connect['time_delta_with_previous_rental_in_minutes'] > 0) & 
                               (df_connect['time_delta_with_previous_rental_in_minutes'] <= 60) & 
                               (df_connect['delay_at_checkout_in_minutes'] > 0)).sum()

# Calculate the percentage
percentage_within_60_minutes_connect = 100 * num_cases_within_60_minutes_connect / prob_cases
# Display the result
print(f"- Percentage of problematic connect cases within 60 minutes: {percentage_within_60_minutes_connect:.2f}%")

# Calculate the percentage of cases within 60 minutes over the total number of rentals
percentage_within_60_minutes_over_total_connect = 100 * num_cases_within_60_minutes_connect / df_connect.shape[0]
# Display the result
print(f"- Percentage of problematic connect cases within 60 minutes over the total of rentals: {percentage_within_60_minutes_over_total_connect:.2f}%")

# Compute the number of rows where the time delta is between 0 and 120 minutes
num_cases_within_120_minutes_connect = ((df_connect['time_delta_with_previous_rental_in_minutes'] > 0) & 
                                (df_connect['time_delta_with_previous_rental_in_minutes'] <= 120) & 
                                (df_connect['delay_at_checkout_in_minutes'] > 0)).sum()

# Calculate the percentage
percentage_within_120_minutes_connect = 100 * num_cases_within_120_minutes_connect / prob_cases
# Display the result
print(f"- Percentage of problematic connect cases within 120 minutes: {percentage_within_120_minutes_connect:.2f}%")

# Calculate the percentage of cases within 120 minutes over the total number of rentals
percentage_within_120_minutes_over_total_connect = 100 * num_cases_within_120_minutes_connect / df_connect.shape[0]
# Display the result
print(f"- Percentage of problematic connect cases within 120 minutes over the total of rentals: {percentage_within_120_minutes_over_total_connect:.2f}%")

# Compute the number of rows where the time delta is between 0 and 240 minutes
num_cases_within_240_minutes_connect = ((df_connect['time_delta_with_previous_rental_in_minutes'] > 0) & 
                                (df_connect['time_delta_with_previous_rental_in_minutes'] <= 240) & 
                                (df_connect['delay_at_checkout_in_minutes'] > 0)).sum()

# Calculate the percentage
percentage_within_240_minutes_connect = 100 * num_cases_within_240_minutes_connect / prob_cases
# Display the result
print(f"- Percentage of problematic connect cases within 240 minutes: {percentage_within_240_minutes_connect:.2f}%")

# Calculate the percentage of cases within 240 minutes over the total number of rentals
percentage_within_240_minutes_over_total_connect = 100 * num_cases_within_240_minutes_connect / df_connect.shape[0]
# Display the result
print(f"- Percentage of problematic connect cases within 240 minutes over the total of rentals: {percentage_within_240_minutes_over_total_connect:.2f}%")



num_cases_within_600_minutes_connect = ((df_connect['time_delta_with_previous_rental_in_minutes'] > 0) & 
                                (df_connect['time_delta_with_previous_rental_in_minutes'] <= 600) & (df['delay_at_checkout_in_minutes']>0) ).sum()

# Calculate the percentage
percentage_within_600_minutes_connect  = 100 * num_cases_within_600_minutes_connect  / prob_cases
# Display the result
print(f"- Percentage of problematic connect cases within 600 minutes: {percentage_within_600_minutes_connect:.2f}%")

# Calculate the percentage of cases within 600 minutes over the total number of rentals
percentage_within_600_minutes_over_total_connect = 100 * num_cases_within_600_minutes_connect / df.shape[0]
# Display the result
print(f"- Percentage of problematic connect cases within 600 minutes over the total of rentals: {percentage_within_600_minutes_over_total_connect:.2f}%")

# Compute the number of rows where the time delta is between 0 and 600 minutes
num_cases_within_720_minutes_connect = ((df_connect['time_delta_with_previous_rental_in_minutes'] > 0) & 
                                (df_connect['time_delta_with_previous_rental_in_minutes'] <= 720) & (df['delay_at_checkout_in_minutes']>0)).sum()

percentage_within_720_minutes_connect = 100 * num_cases_within_720_minutes_connect / prob_cases
# Display the result
st.write(f"- Percentage of problematic connect cases within 720 minutes: {percentage_within_720_minutes_connect:.2f}%")

# Calculate the percentage of cases within 720 minutes over the total number of rentals
percentage_within_720_minutes_over_total_connect = 100 * num_cases_within_720_minutes_connect / df.shape[0]
# Display the result
st.write(f"- Percentage of problematic connect cases within 720 minutes over the total of rentals: {percentage_within_720_minutes_over_total_connect:.2f}%")


# Compute the number of rows where the time delta is between 0 and 30 minutes
num_cases_within_30_minutes_mobile = ((df_mobile['time_delta_with_previous_rental_in_minutes'] > 0) & 
                                       (df_mobile['time_delta_with_previous_rental_in_minutes'] <= 30) & 
                                       (df_mobile['delay_at_checkout_in_minutes'] > 0)).sum()

# Calculate the percentage
percentage_within_30_minutes_mobile = 100 * num_cases_within_30_minutes_mobile / prob_cases
# Display the result
print(f"- Percentage of problematic mobile cases within 30 minutes: {percentage_within_30_minutes_mobile:.2f}%")

# Calculate the percentage of cases within 30 minutes over the total number of rentals
percentage_within_30_minutes_over_total_mobile = 100 * num_cases_within_30_minutes_mobile / df.shape[0]
# Display the result
print(f"Percentage of problematic mobile cases within 30 minutes over the total of rentals: {percentage_within_30_minutes_over_total_mobile:.2f}%")

# Compute the number of rows where the time delta is between 0 and 60 minutes
num_cases_within_60_minutes_mobile = ((df_mobile['time_delta_with_previous_rental_in_minutes'] > 0) & 
                                       (df_mobile['time_delta_with_previous_rental_in_minutes'] <= 60) & 
                                       (df_mobile['delay_at_checkout_in_minutes'] > 0)).sum()

# Calculate the percentage
percentage_within_60_minutes_mobile = 100 * num_cases_within_60_minutes_mobile / prob_cases
# Display the result
print(f"Percentage of problematic mobile cases within 60 minutes: {percentage_within_60_minutes_mobile:.2f}%")

# Calculate the percentage of cases within 60 minutes over the total number of rentals
percentage_within_60_minutes_over_total_mobile = 100 * num_cases_within_60_minutes_mobile / df.shape[0]
# Display the result
print(f"Percentage of problematic mobile cases within 60 minutes over the total of rentals: {percentage_within_60_minutes_over_total_mobile:.2f}%")

# Compute the number of rows where the time delta is between 0 and 120 minutes
num_cases_within_120_minutes_mobile = ((df_mobile['time_delta_with_previous_rental_in_minutes'] > 0) & 
                                        (df_mobile['time_delta_with_previous_rental_in_minutes'] <= 120) & 
                                        (df_mobile['delay_at_checkout_in_minutes'] > 0)).sum()

# Calculate the percentage
percentage_within_120_minutes_mobile = 100 * num_cases_within_120_minutes_mobile / prob_cases
# Display the result
print(f"Percentage of problematic mobile cases within 120 minutes: {percentage_within_120_minutes_mobile:.2f}%")

# Calculate the percentage of cases within 120 minutes over the total number of rentals
percentage_within_120_minutes_over_total_mobile = 100 * num_cases_within_120_minutes_mobile / df.shape[0]
# Display the result
print(f"Percentage of problematic mobile cases within 120 minutes over the total of rentals: {percentage_within_120_minutes_over_total_mobile:.2f}%")

# Compute the number of rows where the time delta is between 0 and 240 minutes
num_cases_within_240_minutes_mobile = ((df_mobile['time_delta_with_previous_rental_in_minutes'] > 0) & 
                                        (df_mobile['time_delta_with_previous_rental_in_minutes'] <= 240) & 
                                        (df_mobile['delay_at_checkout_in_minutes'] > 0)).sum()

# Calculate the percentage
percentage_within_240_minutes_mobile = 100 * num_cases_within_240_minutes_mobile / prob_cases
# Display the result
print(f"Percentage of problematic mobile cases within 240 minutes: {percentage_within_240_minutes_mobile:.2f}%")

# Calculate the percentage of cases within 240 minutes over the total number of rentals
percentage_within_240_minutes_over_total_mobile = 100 * num_cases_within_240_minutes_mobile / df.shape[0]
# Display the result
print(f"Percentage of problematic mobile cases within 240 minutes over the total of rentals: {percentage_within_240_minutes_over_total_mobile:.2f}%")

# Compute the number of rows where the time delta is between 0 and 600 minutes
num_cases_within_600_minutes_mobile = ((df_mobile['time_delta_with_previous_rental_in_minutes'] > 0) & 
                                        (df_mobile['time_delta_with_previous_rental_in_minutes'] <= 600) & 
                                        (df_mobile['delay_at_checkout_in_minutes'] > 0)).sum()

# Calculate the percentage
percentage_within_600_minutes_mobile = 100 * num_cases_within_600_minutes_mobile / prob_cases
# Display the result
print(f"Percentage of problematic mobile cases within 600 minutes: {percentage_within_600_minutes_mobile:.2f}%")

# Calculate the percentage of cases within 600 minutes over the total number of rentals
percentage_within_600_minutes_over_total_mobile = 100 * num_cases_within_600_minutes_mobile / df.shape[0]
# Display the result
print(f"Percentage of problematic mobile cases within 600 minutes over the total of rentals: {percentage_within_600_minutes_over_total_mobile:.2f}%")

# Compute the number of rows where the time delta is between 0 and 720 minutes
num_cases_within_720_minutes_mobile = ((df_mobile['time_delta_with_previous_rental_in_minutes'] > 0) & 
                                        (df_mobile['time_delta_with_previous_rental_in_minutes'] <= 720) & 
                                        (df_mobile['delay_at_checkout_in_minutes'] > 0)).sum()

# Calculate the percentage
percentage_within_720_minutes_mobile = 100 * num_cases_within_720_minutes_mobile / prob_cases
st.write(f"- Percentage of problematic mobile cases within 720 minutes: {percentage_within_720_minutes_mobile:.2f}%")

# Calculate the percentage of cases within 720 minutes over the total number of rentals
percentage_within_720_minutes_over_total_mobile = 100 * num_cases_within_720_minutes_mobile / df.shape[0]
st.write(f"- Percentage of problematic mobile cases within 720 minutes over the total of rentals: {percentage_within_720_minutes_over_total_mobile:.2f}%")

st.write("Therefore:")

st.write("""
- If the feature's scope applies only to connect cars with a maximum threshold time of 720 minutes (12 hours):
  - 720 minutes is the longest delay measured.
  - This may have an impact on 1.05% of the total rentals where problematic situations were verified.
         
  
- If the feature's scope applies to both mobile and connect cars with a maximum threshold time of 720 minutes (12 hours):
  - It may affect {:.2f}% of the total rentals where problematic situations were verified.
         
See visualisations below.
""".format(percentage_prob_cases))



# Data for connect and mobile cars
time_intervals = ['0-30', '0-60', '0-120', '0-240', '0-600', '0-720']

# Example percentages for connect and mobile cases (replace with your actual data)
percentages_connect = [
    percentage_within_30_minutes_connect, 
    percentage_within_60_minutes_connect, 
    percentage_within_120_minutes_connect, 
    percentage_within_240_minutes_connect, 
    percentage_within_600_minutes_connect,
    percentage_within_720_minutes_connect
]

percentages_mobile = [
    percentage_within_30_minutes_mobile, 
    percentage_within_60_minutes_mobile, 
    percentage_within_120_minutes_mobile, 
    percentage_within_240_minutes_mobile, 
    percentage_within_600_minutes_mobile,
    percentage_within_720_minutes_mobile
]

# Create Plotly figure
fig = go.Figure()

# Add bars for connect check-in cases
fig.add_trace(go.Bar(
    x=time_intervals,
    y=percentages_connect,
    name='Connect Check-in',
    marker_color='lightcoral'
))

# Add bars for mobile check-in cases
fig.add_trace(go.Bar(
    x=time_intervals,
    y=percentages_mobile,
    name='Mobile Check-in',
    marker_color='royalblue'
))

# Update the layout
fig.update_layout(
    title='Percentage over total of problematic cases for the different time intervals',
    xaxis_title='Time Interval (minutes)',
    yaxis_title='Percentage (%)',
    barmode='group',  # Group the bars
    xaxis=dict(tickmode='array', tickvals=time_intervals),
    yaxis=dict(range=[0, max(max(percentages_connect), max(percentages_mobile)) + 10])
)

# Show the chart in Streamlit
st.plotly_chart(fig)


# Compute percentages and display results
st.subheader("Analysis of Problematic Cases Based on Time Delta:") 
             
st.subheader("All type of cars")


# Compute the number of cases and percentages
time_intervals = [30, 60, 120, 240, 600, 720]
num_cases_within_intervals = []
percentages_within_intervals = []
percentages_over_total = []

for interval in time_intervals:
    num_cases = ((df['time_delta_with_previous_rental_in_minutes'] > 0) & 
                 (df['time_delta_with_previous_rental_in_minutes'] <= interval) & 
                 (df['delay_at_checkout_in_minutes'] > 0)).sum()
    percentage_within_interval = 100 * num_cases / prob_cases
    percentage_over_total = 100 * num_cases / df.shape[0]
    num_cases_within_intervals.append(num_cases)
    percentages_within_intervals.append(percentage_within_interval)
    percentages_over_total.append(percentage_over_total)

# Plotly figures
fig1 = go.Figure()
fig2 = go.Figure()

# Plot percentages within intervals
fig1.add_trace(go.Bar(
    x=time_intervals,
    y=percentages_within_intervals,
    name='Percentage of Problematic Cases Within Intervals',
    marker_color='royalblue'
))

fig1.update_layout(
    title='Percentage of Problematic Cases Within Different Time Intervals',
    xaxis_title='Time Interval (minutes)',
    yaxis_title='Percentage',
    xaxis=dict(tickmode='array', tickvals=time_intervals, ticktext=[f'{i} min' for i in time_intervals])
)

# Plot percentages over total rentals
fig2.add_trace(go.Bar(
    x=time_intervals,
    y=percentages_over_total,
    name='Percentage of Problematic Cases Over Total Rentals',
    marker_color='lightcoral'
))

fig2.update_layout(
    title='Percentage of Problematic Cases Over Total Rentals',
    xaxis_title='Time Interval (minutes)',
    yaxis_title='Percentage',
    xaxis=dict(tickmode='array', tickvals=time_intervals, ticktext=[f'{i} min' for i in time_intervals])
)

# Streamlit display
st.subheader("Problematic Cases bar charts")

# Display Plotly figures
st.plotly_chart(fig1)
st.write("The interval of 720 (12 hours) covers the maximum delay registered. As the graph shows this interval is equal to the 100% of problematic cases")

st.plotly_chart(fig2)


st.subheader("Different type of cars")
st.subheader("Connect check-in cars vs Mobile check-in cars")
df_mobile = df[df['checkin_type']=='mobile']
df_connect = df[df['checkin_type']=='connect']


# Assuming df contains the column 'checkin_type'
checkin_counts = df['checkin_type'].value_counts()

# Extracting data from value_counts()
total_checkin_counts = checkin_counts.sum()

percentages = (checkin_counts / total_checkin_counts) * 100
labels = percentages.index.tolist()
values = percentages.values.tolist()

# Create the bar chart
fig = go.Figure(
    go.Bar(
        x=labels, 
        y=values,
        marker_color=['skyblue', 'lightcoral'],  # Adjust colors as needed
        text=[f'{val:.2f}%' for val in values],
        textposition='auto'
    )
)

# Customize the layout
fig.update_layout(
    title='Check-in types distribution',
    yaxis_title='Percentage of Check-ins',
    xaxis_title='Check-in Type',
    yaxis=dict(
        range=[0, max(values) + 10] 
))

# Display the chart in Streamlit
st.plotly_chart(fig)

#Fonction for calculating percentages for connect and mobile categories


def calculate_percentages(df, prob_cases, time_intervals, dataset_name):
    percentages_within_intervals = []
    percentages_within_intervals_over_total = []
    
    for interval in time_intervals:
        # Compute the number of rows where the time delta is between 0 and the current interval
        num_cases_within_interval = ((df['time_delta_with_previous_rental_in_minutes'] > 0) & 
                                      (df['time_delta_with_previous_rental_in_minutes'] <= interval) & 
                                      (df['delay_at_checkout_in_minutes'] > 0)).sum()

        # Calculate the percentage within the interval
        percentage_within_interval = 100 * num_cases_within_interval / prob_cases
        percentages_within_intervals.append(percentage_within_interval)

        # Calculate the percentage of cases within the interval over the total number of rentals
        percentage_within_interval_over_total = 100 * num_cases_within_interval / df.shape[0]
        percentages_within_intervals_over_total.append(percentage_within_interval_over_total)
    
    return percentages_within_intervals, percentages_within_intervals_over_total


# Calculate percentages for both datasets
percentages_connect, percentages_connect_over_total = calculate_percentages(df_connect, prob_cases, time_intervals, 'connect')
percentages_mobile, percentages_mobile_over_total = calculate_percentages(df_mobile, prob_cases, time_intervals, 'mobile')

# Create Plotly figure
fig = go.Figure()

# Add bars for connect check-in cases
fig.add_trace(go.Bar(
    x=time_intervals,
    y=percentages_connect,
    name='Connect Check-in',
    marker_color='lightcoral'
))

# Add bars for mobile check-in cases
fig.add_trace(go.Bar(
    x=time_intervals,
    y=percentages_mobile,
    name='Mobile Check-in',
    marker_color='royalblue'
))

# Update the layout
fig.update_layout(
    title='Percentage over problematic cases for the different time intervals',
    xaxis_title='Time Interval (minutes)',
    yaxis_title='Percentage (%)',
    barmode='group',  # Group the bars
    xaxis=dict(tickmode='array', tickvals=time_intervals),
    yaxis=dict(range=[0, max(max(percentages_connect), max(percentages_mobile_over_total)) + 10])
)

# Show the chart in Streamlit
st.plotly_chart(fig)





# Create Plotly figure
fig = go.Figure()

# Add bars for connect check-in cases
fig.add_trace(go.Bar(
    x=time_intervals,
    y=percentages_connect_over_total,
    name='Connect Check-in',
    marker_color='lightcoral'
))

# Add bars for mobile check-in cases
fig.add_trace(go.Bar(
    x=time_intervals,
    y=percentages_mobile_over_total,
    name='Mobile Check-in',
    marker_color='royalblue'
))

# Update the layout
fig.update_layout(
    title='Percentage over total rented cars for the different time intervals',
    xaxis_title='Time Interval (minutes)',
    yaxis_title='Percentage (%)',
    barmode='group',  # Group the bars
    xaxis=dict(tickmode='array', tickvals=time_intervals),
)

# Show the chart in Streamlit
st.plotly_chart(fig)
            
