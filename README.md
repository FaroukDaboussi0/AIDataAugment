## TextAugmentor: Supercharge Your NLP Models with Data Augmentation

**Welcome to TextAugmentor, your ultimate tool for boosting the size and quality of your text data!** Whether you're crafting powerful text classifiers, building impressive question-answering systems, or tackling any other NLP challenge, the strength of your dataset directly impacts your model's performance.

### Why Choose TextAugmentor?

In the world of NLP, the golden rule is "more data is better". But let's be real - acquiring and labeling additional data can be a costly and time-consuming endeavor. 

**Enter data augmentation!** TextAugmentor empowers you to generate synthetic text data from your existing dataset, enhancing its richness and diversity.  

**Here's how TextAugmentor elevates your NLP game:**

* **Effortless Augmentation:** Augment individual texts or entire datasets with ease.
* **Bulk Data Handling:** Process large datasets without breaking a sweat.
* **Customizable Language & Style:** Tailor augmentation to your specific needs - choose the language and style that best suits your project.
* **Flexible File Formats:** Import and export data in CSV, TSV, XLS, XLSX, JSON, and DataFrame formats for seamless integration.
* **Thread-Safe Operations:** Process data safely and efficiently in a multi-threaded environment.
* **Precise Control:** Specify the number of augmentations (recommended range: 2 to 100) to fine-tune your dataset expansion.

### Getting Started:  

**Prerequisites:** 

Before you dive in, To use the Gemini API, you need an API key , head over [here](https://ai.google.dev/gemini-api/docs/api-key?hl=fr) 

**Installation:**

Install the necessary packages:

```bash
pip install AIDataAugment
```

**Usage:**

1. **Initializing TextAugmentor:**

    ```python
    from AIDataAugment.TextAugmentor import TextAugmentor


    # Initialize with your API key
    augmentor = TextAugmentor(api_key="YOUR_API_KEY")
    ```

2. **Augmenting a Single Text:**

    ```python
    text = "Your original text goes here."
    augmented_texts = augmentor.augment_string(text, num_augmentations=5, style="standard", language="EN")
    print(augmented_texts)
    ```

3. **Augmenting an Entire Dataset:**

    You can use the augmentor to augment data in a dataset from a file or a pandas DataFrame. Supported file formats are CSV, TSV, XLS, and XLSX.

    1. Using a file path :

    ```python
    from augmentor import augment

    # File path to your dataset
    file_path = r'Your dataset path.'

    # Column that you want to augment
    column_to_augment = "Example"

    # Number of times you want to augment your data
    total_augmentations = 3

    # Customize your rephrasing style (default: 'standard')
    style = 'standard'

    # Specify the language for augmentation (default: 'EN')
    language = 'EN'

    # Output filename for the augmented data
    output_filename = 'augmented_data.csv'

    # Perform augmentation and save the result to a file
    augmentor.augment(
        file_path=file_path,
        column_to_augment=column_to_augment,
        total_augmentations=total_augmentations,
        style=style,
        language=language,
        output_filename=output_filename
    )
    ```

    2. Using a pandas DataFrame
    ```python
    import pandas as pd
    from augmentor import augment

    # Your pandas DataFrame
    df = pd.read_csv('your_dataset.csv')

    # Column that you want to augment
    column_to_augment = "Example"

    # Number of times you want to augment your data
    total_augmentations = 3

    # Customize your rephrasing style (default: 'standard')
    style = 'standard'

    # Specify the language for augmentation (default: 'EN')
    language = 'EN'

    # Perform augmentation and return the augmented DataFrame
    augmented_df = augmentor.augment(
        dataframe=df,
        column_to_augment=column_to_augment,
        total_augmentations=total_augmentations,
        style=style,
        language=language
    )
    ```
    **Parameters**:
    * **file_path** (str): The path to the dataset file. Supported formats: CSV, TSV, XLS, XLSX.
    * **dataframe** (pd.DataFrame): The pandas DataFrame containing your data.
    * **column_to_augment** (str): The column name to augment.
    * **total_augmentations** (int): The number of times to augment the data.
    * **style** (str, optional): The rephrasing style (default is 'standard').
    * **language** (str, optional): The language for augmentation (default is 'EN').
    * **output_filename** (str, optional): The filename to save the augmented data (only for file-based augmentation).

    **Returns**:
    * **pd.DataFrame**: A DataFrame containing the augmented data (only for DataFrame-based augmentation).
### What Sets TextAugmentor Apart?

* **Simplicity:**  A user-friendly interface for augmenting both individual texts and entire datasets.
* **Adaptability:** Supports multiple languages and augmentation styles to fit your project's requirements.
* **Versatility:** Works seamlessly with various file formats, integrating effortlessly into your existing workflow.
* **Control:**  Specify the desired level of data augmentation with recommendations based on text structure and size.

### Real-World Benefits:

* **Text Translation or Rephrasing:** This tool can also be used for data text translation or rephrasing. Be creative!

* **Boosted Model Performance:** Augmented data enhances model generalization, leading to improved accuracy and robustness.
* **Time & Resource Savings:** No need for manual data collection and labeling, saving you valuable time and resources.
* **Enriched Data Diversity:** Synthetic data introduces variability, making your models more resilient to different text variations.

### Conclusion:

TextAugmentor is your ultimate tool for text data augmentation.  Its powerful features, ease of use, and adaptability empower you to quickly and efficiently expand your dataset, giving your NLP models the edge they need to excel.
## Open Source Contribution:
This is an open-source tool. Don’t hesitate to make it better and contribute! We welcome your contributions to enhance its functionality and usability.



**Happy Augmenting!** 🚀 

