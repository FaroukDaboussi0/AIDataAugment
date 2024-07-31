import re
import sys
import time
import threading
import google.generativeai as genai
import pandas as pd
import json
import logging
import os

class TextAugmentor:
    def __init__(self, api_key):
        self.max_char_limit = 20000
        self.max_char_input_limit = 50000
        self.new_rows = []
        self.column_to_augment = None
        self.lock = threading.Lock()  # Initialize a lock for thread safety
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)
        
        # Configure the API
        genai.configure(api_key=api_key)
        self.safety_settings = [
            {"category": "HARM_CATEGORY_DANGEROUS", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
        self.model = genai.GenerativeModel('gemini-1.5-flash', safety_settings=self.safety_settings)

    def augment_string(self, text, num_augmentations,style = "standard",language="EN"):
        if not text.strip():
            raise Exception("The text is empty. Try with text that contains words.")

        if len(text) > self.max_char_input_limit:
            self.logger.error(f"Text length ({len(text)}) exceeds the maximum allowed character limit ({self.max_char_input_limit}).")
            return
        
        self.language = language
        augmented_texts = []
        text_length = len(text)
        max_augmentations_per_prompt = self._calculate_max_augmentations_per_prompt(text_length)
        remaining_augmentations = num_augmentations
        self.style = style

        while remaining_augmentations > 0:
            num_augmentations = min(max_augmentations_per_prompt, remaining_augmentations)
            prompt = self._build_prompt(text, text_length, num_augmentations)
            response = self._generate_text(prompt)
            attempt = 0

            while (not response or len(response) < text_length * num_augmentations * 0.6) and attempt < 2:
                prompt = self._build_prompt(response, text_length, num_augmentations, task="extend")
                response = self._generate_text(prompt)
                attempt += 1

            if response:
                texts = self._extract_versions(response, num_augmentations)
                augmented_texts.extend(texts)

            remaining_augmentations -= num_augmentations

        return augmented_texts
    
    def _extract_file_format(self, file_path):
        if '.' in file_path:
            return file_path.split('.')[-1].lower()
        else:
            raise ValueError("File path does not have a valid extension.")
        
    def _resume_index(self , file_path):
        if os.path.exists(file_path):
            file_format = self._extract_file_format(file_path)
            if file_format == 'csv':
                df = pd.read_csv(file_path)
                return len(df)
            elif file_format == 'tsv':
                df = pd.read_csv(file_path, delimiter='\t')
                return len(df)
            elif file_format in ['xls', 'xlsx']:
                df= pd.read_excel(file_path)
                return len(df)
            else:
                raise ValueError("Unsupported file format. Please use 'csv', 'tsv', or 'xls/xlsx'.")
        else : 
            return 0
        
    def _load_data(self, file_path=None, dataframe=None):
        if dataframe is not None:
            self.dataframe = dataframe
        elif file_path:
            file_format = self._extract_file_format(file_path)
            if file_format == 'csv':
                self.dataframe = pd.read_csv(file_path)
            elif file_format == 'tsv':
                self.dataframe = pd.read_csv(file_path, delimiter='\t')
            elif file_format in ['xls', 'xlsx']:
                self.dataframe = pd.read_excel(file_path)
            else:
                raise ValueError("Unsupported file format. Please use 'csv', 'tsv', or 'xls/xlsx'.")
        else:
            raise ValueError("Either file_path or dataframe must be provided.")

    def _generate_text(self, text):
        for attempt in range(3):
            try:
                response = self.model.generate_content(text)
                time.sleep(4)
                if not response or not hasattr(response, 'text'):
                    raise ValueError("Invalid operation: The `response.text` quick accessor requires the response to contain a valid `Part`, but none were returned. Please check the `candidate.safety_ratings` to determine if the response was blocked.")
                return response.text
            except ValueError as e:
                self.logger.error(f"Attempt {attempt + 1} failed: {e}")
                if attempt == 2:
                    self.logger.error("Continuing after 3 failed attempts.")
                    return None

    def _build_prompt(self, text, char_count, num_versions, task="generate"):
        if task == "generate":
            output_format = "\n".join([
                f"&&version_{i}&& [Generate a reformulated version of the input text that retains the key information but is expressed differently in the range of {char_count} characters.]"
                for i in range(1, num_versions + 1)
            ])
            prompt = f'''
            Task: Generate a {self.style} rephrased version of the input text, preserving the essential information while expressing it uniquely within approximately {char_count} characters. Ensure the output maintains the original text format without adding any extra titles or markdown.
            language : {self.language}
            Input Text: {text}

            Output Format:
            {output_format}
            '''
        else:
            prompt = f'''
            Task: Extend the text for each &&version&& existing in the text input. The output format should match the original text, no extra titles or markdown.
            language : {self.language}
            Input Text: {text}

            Output Format:
            '''
        return prompt.strip()

    def _sanitize_value(self, value, file_format):
        if isinstance(value, str):
            if file_format == 'json':
                sanitized_value = json.dumps(value)
            elif file_format in ['xls', 'xlsx']:
                sanitized_value = re.sub(r'[,\t\n\r]', ' ', value)
            elif file_format == 'csv':
                sanitized_value = value.replace(',', ' ').replace('\t', ' ').replace('\n', ' ').replace('\r', ' ')
            elif file_format == 'tsv':
                sanitized_value = value.replace('\t', ' ').replace('\n', ' ').replace('\r', ' ')
            else:
                sanitized_value = value.replace('\t', ' ').replace('\n', ' ').replace('\r', ' ')
        else:
            sanitized_value = str(value)  # Ensure value is a string
        return sanitized_value

    def _extract_versions(self, prototype, num_versions):
        texts = []

        for i in range(1, num_versions + 1):
            version_tag = f"&&version_{i}&&"
            start_index = prototype.find(version_tag) + len(version_tag)
            end_index = prototype.find(f"&&version_{i + 1}&&") if i < num_versions else len(prototype)
            text = prototype[start_index:end_index].strip()
            texts.append(text)

        return texts

    def _calculate_max_augmentations_per_prompt(self, text_length):
        max_augmentations = self.max_char_limit // text_length
        return max(1, max_augmentations)

    def _augment_text(self, text, row, column_to_augment, total_augmentations):
        if not text.strip():
            raise Exception("The text is empty. Try with text that contains words.")
        if len(text) > self.max_char_input_limit:
            self.logger.error(f"Text length ({len(text)}) exceeds the maximum allowed character limit ({self.max_char_input_limit}).")
            return
        
        text_length = len(text)
        max_augmentations_per_prompt = self._calculate_max_augmentations_per_prompt(text_length)
        remaining_augmentations = total_augmentations

        while remaining_augmentations > 0:
            num_augmentations = min(max_augmentations_per_prompt, remaining_augmentations)
            prompt = self._build_prompt(text, text_length, num_augmentations)
            response = self._generate_text(prompt)
            attempt = 0

            while (not response or len(response) < text_length * num_augmentations * 0.6) and attempt < 2:
                prompt = self._build_prompt(response, text_length, num_augmentations, task="extend")
                response = self._generate_text(prompt)
                attempt += 1

            if response:
                texts = self._extract_versions(response, num_augmentations)
                with self.lock:  # Ensure thread-safe access to shared resources

                    for augmented_text in texts:
                        new_row = row.copy()
                        new_row[column_to_augment] = augmented_text
                        self.new_rows.append(new_row)
                        self._save_intermediate() 

            remaining_augmentations -= num_augmentations
    def _build_batch_prompt(self, batch, column_to_augment, total_augmentations):
        texts = "\n".join([
            f'''Text {index+1} : {rowt[column_to_augment]}'''
            for index, rowt in enumerate(batch)
        ])
        output = "\n".join([
            f'''&&text_{index + 1}_version_{i+1}&& [Generate a reformulated version of the input text that retains the key information but is expressed differently in the range of {len(rowc[column_to_augment])} characters.]'''
            for index, rowc in enumerate(batch)
            for i in range(total_augmentations)
        ])
        prompt = f'''
        Task: for each Text in the input texts, generate a {self.style} rephrased version of the input texts, preserving the essential information while expressing it uniquely. Ensure the output maintains the original text format without adding any extra titles or markdown .
        Language: {self.language}
        Input Texts: {texts}

        Output Format:
        {output}
        '''
        return prompt
    def __extract_versions_large(self, response, total_augmentations, batch):
        M = []

        for j in range(1, len(batch) + 1):
            texts = []

            for i in range(1, total_augmentations + 1):
                version_tag = f"&&text_{j}_version_{i}&&"
                next_version_tag = f"&&text_{j}_version_{i+1}&&"
                next_batch_tag = f"&&text_{j+1}_version_{1}&&"

                if version_tag in response:
                    start_index = response.find(version_tag) + len(version_tag)
                    if i < total_augmentations and next_version_tag in response:
                        end_index = response.find(next_version_tag)
                    elif i >= total_augmentations and j < len(batch) and next_batch_tag in response:
                        end_index = response.find(next_batch_tag)
                    else:
                        end_index = len(response)
                    text = response[start_index:end_index].strip()
                    texts.append(text)
                else:
                    texts.append(" ")

            M.append(texts)

        return M
    def _process_batch(self, batch, column_to_augment, total_augmentations):
        prompt = self._build_batch_prompt(batch, column_to_augment, total_augmentations)
        response = self._generate_text(prompt)

        if response:
            M = self.__extract_versions_large(response, total_augmentations, batch)

            for i, rowN in enumerate(batch):

                for j in range(total_augmentations):
                    new_row = rowN.copy()
                    new_row[column_to_augment] = M[i][j]
                    self.new_rows.append(new_row)
                    self._save_intermediate() 
                    

    def _process_data(self, column_to_augment, total_augmentations, style="standard", language="EN"):

        if not self.output_filename:
            self.output_df = pd.DataFrame()

        if column_to_augment not in self.dataframe.columns:
            raise ValueError(f"Column '{column_to_augment}' does not exist in the DataFrame.")
        
        self.style = style
        self.language = language
        total_rows = len(self.dataframe)
        self.dataframe['text_length'] = self.dataframe[column_to_augment].apply(lambda x: len(str(x)))
        self.dataframe.sort_values(by='text_length', inplace=True)
        self.dataframe.reset_index(drop=True, inplace=True)
        self.dataframe = self.dataframe.drop(columns='text_length')
        batch = []
        current_batch_char_count = 0
        index = self._resume_index(self.output_filename) // total_augmentations
        self.dataframe = self.dataframe.iloc[index:]

        for gindex, row in self.dataframe.iterrows():

            if column_to_augment not in row:
                self.logger.warning(f"Skipping row {gindex + 1} due to missing column data.")
                continue

            row = row.to_dict()
            text = str(row[column_to_augment])
            text_length = len(text)

            if not text.strip():
                self.logger.warning(f"Skipping row {gindex + 1} due to empty text in column '{column_to_augment}'.")
                continue

            if text_length * total_augmentations >= self.max_char_limit:
                self._augment_text(text, row, column_to_augment, total_augmentations)
                continue

            if current_batch_char_count + text_length <= self.max_char_limit / total_augmentations:
                batch.append(row)
                current_batch_char_count += text_length
                
            else:
                self._process_batch(batch, column_to_augment, total_augmentations)
                batch = [row]
                current_batch_char_count = text_length

            sys.stdout.write(f"\r{gindex + 1} / {total_rows} rows processed ")
            sys.stdout.flush()

        if batch:
            self._process_batch(batch, column_to_augment, total_augmentations)

    def _save_intermediate(self):
        with self.lock:  # Ensure thread-safe access to shared resources

            if self.output_filename :
                file_format = self._extract_file_format(self.output_filename)
                df_new_rows = pd.DataFrame(self.new_rows)
                
                if file_format == 'csv':

                    if os.path.exists(self.output_filename):
                        df_existing = pd.read_csv(self.output_filename)
                        df_combined = pd.concat([df_existing, df_new_rows], ignore_index=True)
                    else:
                        df_combined = df_new_rows
                    df_combined.to_csv(self.output_filename, index=False)
                
                elif file_format == 'tsv':

                    if os.path.exists(self.output_filename):
                        df_existing = pd.read_csv(self.output_filename, sep='\t')
                        df_combined = pd.concat([df_existing, df_new_rows], ignore_index=True)
                    else:
                        df_combined = df_new_rows
                    df_combined.to_csv(self.output_filename, sep='\t', index=False)
                
                elif file_format in ['xls', 'xlsx']:

                    if os.path.exists(self.output_filename):
                        df_existing = pd.read_excel(self.output_filename)
                        df_combined = pd.concat([df_existing, df_new_rows], ignore_index=True)
                    else:
                        df_combined = df_new_rows
                    df_combined.to_excel(self.output_filename, index=False)
                
                else:
                    raise ValueError("Unsupported file format. Please use 'csv', 'tsv', or 'xls/xlsx'.")
                
            else : 
                df_new_rows = pd.DataFrame(self.new_rows)  
                self.output_df = pd.concat([self.output_df, df_new_rows])

            self.new_rows = []  # Clear the new_rows after saving

    def augment(self, file_path=None, dataframe=None, column_to_augment=None, total_augmentations=1, style="standard", language="EN", output_filename=None):

        if output_filename is not None and self._extract_file_format(output_filename) not in ["csv","tsv","xls","xlsx"] :
            raise ValueError("Unsupported output file format. Please use 'csv', 'tsv', or 'xls/xlsx'.")
        
        self.output_filename = output_filename

        # Load data
        if file_path is None and dataframe is None:
            raise ValueError("You must pass either a data frame or a file path.")

        if file_path is not None and dataframe is not None:
            raise ValueError("You can pass either a data frame or a file path, not both.")
        
        if dataframe is not None:
            self._load_data(dataframe=dataframe)
        elif file_path is not None:
            self._load_data(file_path=file_path)
        
        # Process data
        self._process_data(column_to_augment=column_to_augment, total_augmentations=total_augmentations, style=style, language=language)

        if output_filename is None:
            return self.output_df
   