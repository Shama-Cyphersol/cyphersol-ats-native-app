from .CashFlowNetwork import CashFlowNetwork
import pandas as pd


def create_network_graph(result):
        try:
            # df = result["cummalative_df"]["process_df"]
            # filtered_df = df[['Name', "Value Date",'Debit', 'Credit', 'Entity']].dropna(subset=['Entity'])
            # threshold = 10000
            # filtered_df = df[(df['Debit'] >= threshold) | (df['Credit'] >= threshold)]
            # return CashFlowNetwork(data=filtered_df)
            process_df = result["cummalative_df"]["process_df"]
            entity_freq_df = result["cummalative_df"]["entity_df"]
            
            # Convert entity frequency data to a dictionary for easier lookup
            # Assuming the first column is 'Entity' and second is 'Frequency'
            entity_freq_dict = dict(zip(entity_freq_df.iloc[:, 0], entity_freq_df.iloc[:, 1]))
            
            # Get base filtered dataframe with required columns and non-null entities
            filtered_df = process_df[['Name', 'Value Date', 'Debit', 'Credit', 'Entity']].dropna(subset=['Entity'])
            
            # Filter based on entity frequency
            # min_frequency = 30
            # filtered_df = filtered_df[filtered_df['Entity'].map(lambda x: entity_freq_dict.get(x, 0) > min_frequency)]
            
            return CashFlowNetwork(data=filtered_df)
        
        except Exception as e:
            print("Error",e)
            # import a excel
            df  = pd.read_excel("src/data/network_process_df.xlsx")
            filtered_df = df[['Name', "Value Date",'Debit', 'Credit', 'Entity']].dropna(subset=['Entity'])
            threshold = 10000
            filtered_df = df[(df['Debit'] >= threshold) | (df['Credit'] >= threshold)]
            return CashFlowNetwork(data=filtered_df)