## NEWS CLASSIFICATION

### Introduction:

The classification model for News is built using the pretrained language model [PhoBERT](https://github.com/VinAIResearch/PhoBERT) public by VinAIRearch. 
Pre-trained **PhoBERT** models are the state-of-the-art language models for Vietnamese:

- Two PhoBERT versions of **base** and **large** are the first public large-scale monolingual language models pre-trained for Vietnamese. PhoBERT pre-training approach is based on RoBERTa which optimizes the BERT pre-training procedure for more robust performance.
- PhoBERT outperforms previous monolingual and multilingual approaches, obtaining new state-of-the-art performances on four downstream Vietnamese NLP tasks of Part-of-speech tagging, Dependency parsing, Named-entity recognition and Natural language inference.
The general architecture and experimental results of PhoBERT can be found in [this paper](https://www.aclweb.org/anthology/2020.findings-emnlp.92/)

- Pre-trained models

    Model | #params | Arch.	 | Pre-training data
    ---|---|---|---
    `vinai/phobert-base` | 135M | base | 20GB  of texts
    `vinai/phobert-large` | 370M | large | 20GB  of texts

The classification model for News is built on pretrained phoBERT in combination with the classication model of transformers library developed by HuggingFace.


### For Development:


#### I. Prepare environment

If you don't have Anaconda3 in your system, then you can use the link below to get it done.

- [Install Anaconda3 on Ubuntu 18.04](https://www.digitalocean.com/community/tutorials/how-to-install-anaconda-on-ubuntu-18-04-quickstart)

- Create a enviroment: `conda create --name py36 python=3.6.9`
  
- Then activate your new environment: `source activate py36`

- Install denpendency library: `pip install -r requirements.txt`

#### II. Prepare dataset 

-  You need to prepare your data as a file `.csv format`. The data consists of 4 fields similar to the data in the database. Where, the Field **text** is combined by the Field **title** and Field **brief_content** used to train the model. Field **label** is the label of the data that has been labeled. The details are described below:

title | brief_content | content | text | label
--- | --- | --- | --- | --- 
Text_1 | Text_2 | Text_3 | Text_1 + Text_2 | Text 4


#### III. Training the model

- To the training the model, use the following code:

```py
from classifier import Classifier

classifier = Classifier(pretrained="vinai/phobert-base")
classifier.train(
    train_path='./data/news/news_train_reviewed.csv', 
    test_path='./data/news/news_test_reviewed.csv', 
    text_col='text', 
    label_col='category', 
    bs=16, 
    epochs=1, 
    lr=1e-5, 
    is_normalize=True
)
```

The model is then stored in the file name **best_model.model** in *.zip* file format.


#### IV. Inference a given sample

- To the inference a given sample, use the following code: 

```py
from classifier import Classifier

classifier = Classifier(model_path='./models/phobert_epoch_1.model')
pred = classifier.predict(sample='hello')
print(pred)
```

- **Note**: In the current model, *sample* is the corresponding Field **text** in the dataset described above. That is, the **text** is the addition of string between **title** and **brief_content**.