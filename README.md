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
from TextAugmentor import TextAugmentor

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
    1. Basic usage exemple :

```python
import pandas as pd

# Load your data
data = pd.read_csv("your_dataset.csv")

# Load your data 
augmentor.load_data(dataframe=data)

augmentor.process_data(
            column_to_augment="text_column", 
            total_augmentations=5,
            style="standard",
            language="EN")

# Output file format supported: csv, tsv, Json,  xls and xlsx
augmentor.save_data("augmented_dataset.csv")
```

2. Additional Features
```python
# Input file format supported: csv, tsv, xls and xlsx
augmentor.load_data(file_path="your_dataset.csv") 

augmentor.process_data(
        column_to_augment="text_column", 
        total_augmentations=5,
        style="creative",  # or " formal" or any style you want
        language="عربية"  # Supported languages are many; see Geminy 1.5 Flash documentation
)

df = augmentor.save_data()  # Leave it empty to return a DataFrame

```

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

