from utils.dynamic_table import DynamicDataTable
import pickle
def create_bidirectional_analysis(result):

    dummy_data = None
    with open("src/data/dummy/bidirectional.pkl", 'rb') as f:
        dummy_data= pickle.load(f)

    bidirectional_analysis_table = DynamicDataTable(
        # df=result["cummalative_df"]["bidirectional_analysis"],
        df=dummy_data,
        # title="Link Analysis Data Table",  # Optional
        rows_per_page=10 , # Optional,
    )
    # link_analysis_table.create_table(content_layout)
    return bidirectional_analysis_table