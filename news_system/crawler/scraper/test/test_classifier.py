from classifier import Classifier
from utils import normalize


## TEST TRAIN MODEL 
classifier = Classifier(pretrained="vinai/phobert-base")
classifier.train(
    train_path='./data/news/news_train_reviewed.csv', 
    test_path='./data/news/news_test_reviewed.csv', 
    text_col='text', 
    label_col='category', 
    bs=16, 
    epochs=1,  ## epochs=5 
    lr=1e-5, 
    is_normalize=True
)

## TEST INFERENCE
classifier = Classifier(model_path='./models/phobert_epoch_1.model')
pred = classifier.predict(sample='hello')
print(pred)
