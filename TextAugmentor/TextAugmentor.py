import re
import sys
import time
import threading
import google.generativeai as genai
import pandas as pd
import json
import logging

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
        max_augmentations_per_prompt = self.calculate_max_augmentations_per_prompt(text_length)
        remaining_augmentations = num_augmentations
        self.style = style
        while remaining_augmentations > 0:
            num_augmentations = min(max_augmentations_per_prompt, remaining_augmentations)
            prompt = self.build_prompt(text, text_length, num_augmentations)
            response = self.generate_text(prompt)
            attempt = 0

            while (not response or len(response) < text_length * num_augmentations * 0.6) and attempt < 2:
                prompt = self.build_prompt(response, text_length, num_augmentations, task="extend")
                response = self.generate_text(prompt)
                attempt += 1

            if response:
                texts = self.extract_versions(response, num_augmentations)
                augmented_texts.extend(texts)

            remaining_augmentations -= num_augmentations

        return augmented_texts
    
    def extract_file_format(self, file_path):
        if '.' in file_path:
            return file_path.split('.')[-1].lower()
        else:
            raise ValueError("File path does not have a valid extension.")

    def load_data(self, file_path=None, dataframe=None):
        if dataframe is not None:
            self.dataframe = dataframe
        elif file_path:
            file_format = self.extract_file_format(file_path)
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

    def generate_text(self, text):
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

    def build_prompt(self, text, char_count, num_versions, task="generate"):
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

    def sanitize_value(self, value, file_format):
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

    def extract_versions(self, prototype, num_versions):
        texts = []
        for i in range(1, num_versions + 1):
            version_tag = f"&&version_{i}&&"
            start_index = prototype.find(version_tag) + len(version_tag)
            end_index = prototype.find(f"&&version_{i + 1}&&") if i < num_versions else len(prototype)
            text = prototype[start_index:end_index].strip()
            texts.append(text)
        return texts

    def calculate_max_augmentations_per_prompt(self, text_length):
        max_augmentations = self.max_char_limit // text_length
        return max(1, max_augmentations)

    def augment_text(self, text, row, column_to_augment, total_augmentations):
        if not text.strip():
            raise Exception("The text is empty. Try with text that contains words.")
        if len(text) > self.max_char_input_limit:
            self.logger.error(f"Text length ({len(text)}) exceeds the maximum allowed character limit ({self.max_char_input_limit}).")
            return
        
        text_length = len(text)
        max_augmentations_per_prompt = self.calculate_max_augmentations_per_prompt(text_length)
        remaining_augmentations = total_augmentations

        while remaining_augmentations > 0:
            num_augmentations = min(max_augmentations_per_prompt, remaining_augmentations)
            prompt = self.build_prompt(text, text_length, num_augmentations)
            response = self.generate_text(prompt)
            attempt = 0
            while (not response or len(response) < text_length * num_augmentations * 0.6) and attempt < 2:
                prompt = self.build_prompt(response, text_length, num_augmentations, task="extend")
                response = self.generate_text(prompt)
                attempt += 1
            if response:
                texts = self.extract_versions(response, num_augmentations)
                with self.lock:  # Ensure thread-safe access to shared resources
                    for augmented_text in texts:
                        new_row = row.copy()
                        new_row[column_to_augment] = augmented_text
                        self.new_rows.append(new_row)

            remaining_augmentations -= num_augmentations
            

    def process_data(self, column_to_augment, total_augmentations,style = "standard",language="EN"):
        if column_to_augment not in self.dataframe.columns:
            raise ValueError(f"Column '{column_to_augment}' does not exist in the DataFrame.")
        self.style = style
        self.column_to_augment = column_to_augment 
        self.language = language
        total_rows = len(self.dataframe)
        for index, row in self.dataframe.iterrows():
            if column_to_augment not in row:
                self.logger.warning(f"Skipping row {index + 1} due to missing column data.")
                continue
            row = row.to_dict()
            text = row[column_to_augment]
            if not text.strip():  # Check if the text is empty or only contains whitespace
                self.logger.warning(f"Skipping row {index + 1} due to empty text in column '{column_to_augment}'.")
                continue
            sys.stdout.write(f"\r{index + 1} / {total_rows}")
            sys.stdout.flush()
            self.augment_text(text, row, column_to_augment, total_augmentations)
        print()    
        self.logger.info("\nData augmentation complete.")

    def save_data(self, output_filename=None):
        if output_filename is None:
            df = pd.DataFrame(self.new_rows)
            return df
        else : 
            file_format = self.extract_file_format(output_filename)
            with self.lock:  # Ensure thread-safe access to shared resources
                if file_format == 'csv':
                    df = pd.DataFrame(self.new_rows)
                    df.to_csv(output_filename, index=False)
                elif file_format == 'tsv':
                    df = pd.DataFrame(self.new_rows)
                    df.to_csv(output_filename, sep='\t', index=False)
                elif file_format in ['xls', 'xlsx']:
                    df = pd.DataFrame(self.new_rows)
                    df.to_excel(output_filename, index=False)
                else:
                    raise ValueError("Unsupported file format. Please use 'csv', 'tsv', or 'xls/xlsx'.")
                self.logger.info(f"Data saved to {output_filename}.")
