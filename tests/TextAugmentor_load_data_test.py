import os
import tempfile
import unittest
import pandas as pd
from TextAugmentor.TextAugmentor import TextAugmentor  # Adjust the import based on your project structure

class TestTextAugmentor(unittest.TestCase):

    def setUp(self):
        # Use a mock API key for testing
        self.augmentor = TextAugmentor(api_key="fake-api-key")

    def test_load_data_csv(self):
        # Create a temporary CSV file with a correct extension
        with tempfile.NamedTemporaryFile(delete=False, mode='w', newline='', suffix='.csv', encoding='utf-8') as temp_csv:
            temp_csv.write("column1,column2\nvalue1,value2\n")
            temp_csv_path = temp_csv.name
        
        try:
            self.augmentor.load_data(file_path=temp_csv_path)
            self.assertIsInstance(self.augmentor.dataframe, pd.DataFrame)
            self.assertEqual(self.augmentor.dataframe.shape[0], 1)  # 1 row of data
        finally:
            os.remove(temp_csv_path)  # Clean up

    def test_load_data_tsv(self):
        # Create a temporary TSV file with a correct extension
        with tempfile.NamedTemporaryFile(delete=False, mode='w', newline='', suffix='.tsv', encoding='utf-8') as temp_tsv:
            temp_tsv.write("column1\tcolumn2\nvalue1\tvalue2\n")
            temp_tsv_path = temp_tsv.name
        
        try:
            self.augmentor.load_data(file_path=temp_tsv_path)
            self.assertIsInstance(self.augmentor.dataframe, pd.DataFrame)
            self.assertEqual(self.augmentor.dataframe.shape[0], 1)  # 1 row of data
        finally:
            os.remove(temp_tsv_path)  # Clean up

    def test_load_data_xlsx(self):
        # Create a temporary Excel file with a correct extension
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx', mode='w', newline='', encoding='utf-8') as temp_xlsx:
            df = pd.DataFrame({"column1": ["value1"], "column2": ["value2"]})
            df.to_excel(temp_xlsx.name, index=False)
            temp_xlsx_path = temp_xlsx.name
        
        try:
            self.augmentor.load_data(file_path=temp_xlsx_path)
            self.assertIsInstance(self.augmentor.dataframe, pd.DataFrame)
            self.assertEqual(self.augmentor.dataframe.shape[0], 1)  # 1 row of data
        finally:
            os.remove(temp_xlsx_path)  # Clean up

    def test_load_data_unsupported_format(self):
        with self.assertRaises(ValueError) as context:
            self.augmentor.load_data(file_path="unsupported_file_format.docx")
        self.assertTrue("Unsupported file format. Please use 'csv', 'tsv', or 'xls/xlsx'." in str(context.exception))

    def test_load_data_missing_arguments(self):
        with self.assertRaises(ValueError) as context:
            self.augmentor.load_data()
        self.assertTrue("Either file_path or dataframe must be provided." in str(context.exception))

    def test_load_data_dataframe(self):
        df = pd.DataFrame({"column1": ["value1"], "column2": ["value2"]})
        self.augmentor.load_data(dataframe=df)
        self.assertIsInstance(self.augmentor.dataframe, pd.DataFrame)
        self.assertEqual(self.augmentor.dataframe.shape[0], 1)  # 1 row of data

if __name__ == '__main__':
    unittest.main()