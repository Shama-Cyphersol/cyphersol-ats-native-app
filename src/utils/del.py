
import pandas as pd

def cumulative_bidirectional_analysis( df):
    # Sort the DataFrame by Value Date
    df['Value Date'] = pd.to_datetime(df['Value Date'])
    # df = df.sort_values(by='Value Date').reset_index(drop=True)
    # Define unique people
    people = df['Name'].unique()
    # Set to keep track of already processed pairs
    processed_pairs = set()
    # List to store bidirectional analysis results
    bidirectional_results = []

    # Iterate through each pair of people
    for i, person in enumerate(people):
        for j in range(i + 1, len(people)):
            entity = people[j]
            # Create a sorted tuple to represent the pair
            pair = tuple(sorted([person, entity]))
            # Skip if this pair has already been processed
            if pair in processed_pairs:
                continue
            # Mark this pair as processed
            processed_pairs.add(pair)
            # Filter transactions involving the pair (both directions: person as Name and entity as Entity or vice versa)
            temp_df = df[((df['Name'] == person) & (df['Entity'] == entity)) | ((df['Name'] == entity) & (df['Entity'] == person))]
            # Print temp_df for inspection
            # print(f"Temp DataFrame for {person} and {entity}:")
            # print(temp_df)
            # print("@" * 30)
            if temp_df.empty:
                continue
            # The first row of Value Date column in temp_df is the start date for the analysis
            start_date = temp_df['Value Date'].iloc[0]
            end_date = temp_df['Value Date'].iloc[-1]

            # Calculate totals and net flow
            total_credit_amount = temp_df[temp_df['Credit'] > 0]['Credit'].sum()
            total_debit_amount = temp_df[temp_df['Debit'] > 0]['Debit'].sum()
            total_credit_transactions = len(temp_df[temp_df['Credit'] > 0])
            total_debit_transactions = len(temp_df[temp_df['Debit'] > 0])
            net_exchange = total_credit_amount - total_debit_amount

            # Calculate average amount exchanged
            total_transactions = total_credit_transactions + total_debit_transactions
            if total_transactions > 0:
                average_amount_exchanged = (total_credit_amount + total_debit_amount) / total_transactions
            else:
                average_amount_exchanged = 0

            # Calculate median and standard deviation of transaction amounts
            all_transactions = temp_df[['Credit', 'Debit']].stack().reset_index(drop=True)
            median_amount_exchanged = all_transactions.median() if not all_transactions.empty else 0
            std_dev_amount_exchanged = all_transactions.std() if not all_transactions.empty else 0

            # Determine highest amount exchanged and its type
            highest_credit = temp_df['Credit'].max() if not temp_df['Credit'].isna().all() else 0
            highest_debit = temp_df['Debit'].max() if not temp_df['Debit'].isna().all() else 0
            if highest_credit >= highest_debit:
                highest_amount_exchanged = highest_credit
                highest_amount_type = 'Credit'
            else:
                highest_amount_exchanged = highest_debit
                highest_amount_type = 'Debit'

            # Determine first and last transaction dates
            first_transaction_date = start_date
            last_transaction_date = end_date

            # Append the result to the list
            bidirectional_results.append({
                'Entity One': pair[0],
                'Entity Two': pair[1],
                'Total Credit Transactions': total_credit_transactions,
                'Total Debit Transactions': total_debit_transactions,
                'Total Credit Amount': total_credit_amount,
                'Total Debit Amount': total_debit_amount,
                'Net Exchange (Credit - Debit)': net_exchange,
                'Average Amount Exchanged': average_amount_exchanged,
                'Median Amount Exchanged': median_amount_exchanged,
                'Highest Amount Exchanged': highest_amount_exchanged,
                'First Transaction Date': first_transaction_date,
                'Last Transaction Date': last_transaction_date
            })
    
    # Convert the list to a DataFrame
    bidirectional_results_df = pd.DataFrame(bidirectional_results)
    return bidirectional_results_df


import pandas as pd

# Sample DataFrames for Alpha, Beta, Gamma
# Sample DataFrames for Alpha, Beta, Gamma, and new entities Delta, Epsilon
# Sample DataFrames for Alpha, Beta, Gamma, and new entities Delta, Epsilon
data = {
    'Value Date': [
        '2024-04-01', '2024-04-03', '2024-04-04', '2024-04-05', '2024-04-06',
        '2024-04-07', '2024-04-08', '2024-04-09', '2024-04-01', '2024-04-04',
        '2024-04-05', '2024-04-06', '2024-04-06',  '2024-04-07', '2024-04-08', '2024-04-02',
        '2024-04-03', '2024-04-04', '2024-04-05', '2024-04-06', '2024-04-07',
        '2024-04-08', '2024-04-09', '2024-04-10', '2024-04-11', '2024-04-12',
        '2024-04-13', '2024-04-14', '2024-04-15', '2024-04-16', '2024-04-17',
        # Manually added transfers between entities
        '2024-04-03', '2024-04-05', '2024-04-06', '2024-04-07', '2024-04-08',
        '2024-04-09', '2024-04-10', '2024-04-11', '2024-04-12'
    ],
    'Name': [
        'Alpha', 'Alpha', 'Alpha', 'Alpha', 'Alpha', 'Alpha', 'Alpha', 'Alpha', 'Beta',
        'Beta', 'Beta', 'Beta', 'Beta', 'Beta', 'Beta', 'Gamma', 'Gamma', 'Gamma', 'Gamma', 'Gamma',
        'Gamma', 'Delta', 'Delta', 'Delta', 'Delta', 'Delta', 'Epsilon', 'Epsilon', 'Epsilon',
        'Epsilon', 'Epsilon',
        # Manually added transfers between entities
        'Alpha', 'Beta', 'Gamma', 'Delta', 'Epsilon', 'Beta', 'Gamma', 'Delta', 'Alpha'
    ],
    'Description': [
        'Opening Balance', 'Credit from Beta', 'Groceries', 'Electricity Bill', 'Dinner',
        'Fuel', 'Online Shopping', 'Gift to Beta', 'Opening Balance', 'Credit from Gamma',
        'Shopping', 'Medical Expense', 'Salary Credit', 'Subscription', 'Gift to Alpha', 'Opening Balance',
        'Credit from Alpha', 'Groceries', 'Travel Expense', 'Dining', 'Gift to Beta',
        'Opening Balance', 'Credit from Epsilon', 'Travel', 'Car Maintenance', 'Medical Expense',
        'Opening Balance', 'Credit from Delta', 'Home Renovation', 'Shopping', 'Gift to Gamma',
        # Manually added transfers between entities
        'Transfer to Beta', 'Transfer to Gamma', 'Transfer to Delta', 'Transfer to Epsilon',
        'Transfer to Beta', 'Transfer to Gamma', 'Transfer to Delta', 'Transfer to Alpha', 'Transfer to Beta'
    ],
    'Debit': [
        0, 0, 200, 150, 100, 50, 300, 100, 0, 0, 200, 300, 0, 100, 150, 0, 0, 250, 100, 150, 200,
        0, 0, 300, 200, 150, 0, 0, 500, 300, 100,
        # Manually added transfers between entities
        500, 1000, 1500, 2000, 2500, 1000, 1500, 2000, 500
    ],
    'Credit': [
        0, 1000, 0, 0, 0, 0, 0, 0, 0, 500, 0, 0, 50000, 0, 0, 0, 10000, 0, 0, 0, 0,
        0, 2000, 0, 0, 0, 0, 3000, 0, 0, 0,
        # Manually added transfers between entities
      0, 0, 0, 0, 0, 0, 0, 0, 0
    ],
    'Entity': [
        'poojan', 'Beta', 'sanjay', 'gar', 'hdfc', 'bigga', None, 'Beta', None, 'Gamma', None, 'bihar', 'cyphersol', None, 'Alpha', None, 'Alpha',
        None, 'raj', None, 'Beta', None, 'Epsilon', None, 'google', 'clone', None, 'Delta', 'openai', None, 'Gamma',
        # Manually added transfers between entities
        'Beta', 'Gamma', 'Delta', 'Epsilon', 'Beta', 'Gamma', 'Delta', 'Alpha', 'Beta'
    ]
}

# Create DataFrame
group_df = pd.DataFrame(data)

def custom_sort(df):
    # Get the unique 'Name' values and their first appearance index
    unique_names = df.drop_duplicates(subset="Name", keep="first").set_index("Name")[
        "Value Date"].sort_values().index

    # Create a categorical type with the unique names in the desired order
    df["Name"] = pd.Categorical(df["Name"], categories=unique_names, ordered=True)

    # Sort by 'Name' first based on the unique order, then by 'Value Date'
    sorted_df = df.sort_values(by=["Name", "Value Date"]).reset_index(drop=True)
    return sorted_df

# Convert Value Date to datetime
# group_df = custom_sort(group_df)
# group_df['Value Date'] = pd.to_datetime(group_df['Value Date'])

# print(group_df.head())
# test = cumulative_bidirectional_analysis(group_df)

# print(test.shape)
# import pickle

# def save_result():
#     with open("src/data/dummy/bidirectional.pkl", 'wb') as f:
#         pickle.dump(test, f)

# save_result()