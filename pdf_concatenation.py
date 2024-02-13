import pandas as pd
import numpy as np

import os

if __name__ == "__main__":
    df = pd.read_csv("./pdf_extract_output/text_dataset_all_inputs.csv", sep=';', encoding='utf-8-sig')

    df_sorted = df.sort_values(by=['document_name', 'page_nb'])
    groups = df.groupby(['page_nb', 'date', 'document_name'])

    concatenated_content = []

    for (page_nb, date, document_name), group in groups:
        group['group_10'] = np.arange(len(group)) // 10
        subgroups = group.groupby('group_10')
        
        for _, subgroup in subgroups:
            content = ''.join(subgroup['content'].tolist())
            concatenated_content.append({
                'page_nb': page_nb,
                'date': date,
                'document_name': document_name,
                'content': content
            })

    concatenated_df = pd.DataFrame(concatenated_content)

    concatenated_df = concatenated_df.sort_values(by=['document_name', 'page_nb'])

    concatenated_df.to_csv(os.path.join(os.environ.get('OUTPUT_FOLDER_PATH'), 'chunks_dataset.csv'), index=False, sep=';', encoding='utf-8-sig')
