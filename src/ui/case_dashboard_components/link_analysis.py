from utils.dynamic_table import DynamicDataTable

def create_link_analysis(result):
    link_analysis_table = DynamicDataTable(
        df=result["cummalative_df"]["link_analysis_df"],
        # title="Link Analysis Data Table",  # Optional
        rows_per_page=10 , # Optional,
        # table_for = "link_analysis",
        
    )
    return link_analysis_table
    # link_analysis_table.create_table(content_layout)
    # return link_analysis_table.create_table()