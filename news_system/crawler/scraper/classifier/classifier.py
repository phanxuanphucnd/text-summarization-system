import os
import torch
import random
import numpy as np
import pandas as pd

from tqdm import tqdm
from pprint import pprint
from typing import List, Text, Any
from torch.utils.data import TensorDataset
from torch.utils.data import DataLoader, RandomSampler, SequentialSampler

from transformers import AutoModel, AutoTokenizer
from transformers import AutoModelForSequenceClassification
from transformers import AdamW, get_linear_schedule_with_warmup
from sklearn.metrics import f1_score, accuracy_score, recall_score, precision_score, classification_report

from .utils import normalize, normalize_df, get_metric, fill_text


seed_val = 17
random.seed(seed_val)
np.random.seed(seed_val)
torch.manual_seed(seed_val)
torch.cuda.manual_seed_all(seed_val)

class Classifier:
    """A Classifier class for News classification problem. """
    def __init__(self, model_path=None, pretrained="vinai/phobert-base"):
        """Initialize a Classifier class 

        :param model_path: (str) Path to the pretrained model Classifier
        :param pretrained: (str) The pretrained LM model, using for training the Classifier model

        """
        self.pretrained = pretrained
        self.model_path = model_path
        self.label_dict = {}

        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.tokenizer = AutoTokenizer.from_pretrained(self.pretrained)
        if self.model_path:
            self.load(path=self.model_path)
    
    def train(
        self, 
        train_path: Text=None, 
        test_path: Text=None,
        text_col: Text='text', 
        label_col: Text='label', 
        bs: int=32, 
        lr: float=1e-5, 
        eps: float=1e-8, 
        epochs: int=10,
        is_normalize: bool=False, 
        name: str='best_model', 
        **kwargs
    ):
        """Training a Classifier model

        :param train_path: Path to the training data (.csv format)
        :param test_path: Path to the test data (.csv format)
        :param text_col: The column name of text field
        :param label_col: The column name of label field
        :param bs: Batch size (default: 32)
        :param lr: Learning rate (default: 1e-5)
        :param eps: Epsilon (default: 1e-8)
        :param epochs: The number of epochs training (default: 10)
        :param is_normalize: If True nornamlize data (default: True)
        :param fill_text: If True, fill `text` field in DataFrame read from train_path (Use when field `text` in train_path not exists.)
        :param name: The name file to save model (default: best_model)

        """

        ## PRE-PROCESSING DATA
        train_df = None
        if train_path:
            train_df = pd.read_csv(train_path, encoding='utf-8')
            if not text_col in train_df.columns:
                train_df = fill_text(train_df)
            if is_normalize:
                train_df = normalize_df(
                    train_df, col=text_col, rm_url=True, rm_emoji=True, rm_special_characters=True)
        else:
            raise ValueError(f"'train_path' must be not None values ! ")
        
        test_df = None
        if test_path:
            test_df = pd.read_csv(test_path, encoding='utf-8')
            if not text_col in test_df.columns:
                test_df = fill_text(test_df)
            if is_normalize:
                test_df = normalize_df(
                    test_df, col=text_col, rm_url=True, rm_emoji=True, rm_special_characters=True)

        labels = train_df[label_col].unique()


        self.label_dict = {}
        for index, label in enumerate(labels):
            self.label_dict[label] = index

        print(f"\n- label_dic: {self.label_dict}\n")
            
        if train_df is not None:
            train_df[label_col] = train_df[label_col].replace(self.label_dict)            
            encoded_data_train = self.tokenizer.batch_encode_plus(
                train_df[text_col].values, 
                add_special_tokens=True, 
                return_attention_mask=True, 
                pad_to_max_length=True, 
                max_length=256, 
                return_tensors='pt', 
                truncation=True
            )

            input_ids_train = encoded_data_train['input_ids']
            attention_masks_train = encoded_data_train['attention_mask']
            labels_train = torch.tensor(train_df[label_col].values)
            dataset_train = TensorDataset(input_ids_train, attention_masks_train, labels_train)

            print(f"\n- Length of Train set={len(dataset_train)}")

            dataloader_train = DataLoader(
                dataset_train, 
                sampler=RandomSampler(dataset_train), 
                batch_size=bs
            )

        if test_df is not None:
            test_df[label_col] = test_df[label_col].replace(self.label_dict)
            encoded_data_val = self.tokenizer.batch_encode_plus(
                test_df[text_col].values, 
                add_special_tokens=True, 
                return_attention_mask=True, 
                pad_to_max_length=True, 
                max_length=256, 
                return_tensors='pt', 
            )

            input_ids_val = encoded_data_val['input_ids']
            attention_masks_val = encoded_data_val['attention_mask']
            labels_val = torch.tensor(test_df[label_col].values)
            dataset_val = TensorDataset(input_ids_val, attention_masks_val, labels_val)
            print(f"\n- Length of Test set={len(dataset_val)} \n")

            dataloader_validation = DataLoader(dataset_val, 
                                   sampler=SequentialSampler(dataset_val), 
                                   batch_size=bs)

        self.model = AutoModelForSequenceClassification.from_pretrained(self.pretrained, 
                                                            num_labels=len(self.label_dict), 
                                                            output_attentions=False, 
                                                            output_hidden_states=False)

        self.model.to(self.device)

        print(f"\n- START TRAINING MODEL ...\n")
        
        self.optimizer = AdamW(self.model.parameters(), lr=lr, eps=eps)
        self.scheduler = get_linear_schedule_with_warmup(self.optimizer, num_warmup_steps=0, num_training_steps=len(dataloader_train)*epochs)

        BEST_METRIC = 0.0

        for epoch in tqdm(range(1, epochs+1)):
            self.model.train()
            
            loss_train_total = 0

            progress_bar = tqdm(dataloader_train, desc='Epoch {:1d}'.format(epoch), leave=False, disable=False)
            for batch in progress_bar:

                self.model.zero_grad()
                
                batch = tuple(b.to(self.device) for b in batch)
                
                inputs = {
                    'input_ids':      batch[0],
                    'attention_mask': batch[1],
                    'labels':         batch[2],
                }       

                outputs = self.model(**inputs)
                
                loss = outputs[0]
                loss_train_total += loss.item()
                loss.backward()

                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)

                self.optimizer.step()
                self.scheduler.step()
                
                progress_bar.set_postfix({'training_loss': '{:.3f}'.format(loss.item()/len(batch))})
                
            if not os.path.exists('models/'):
                os.mkdir('models/')
                
            tqdm.write(f'\nEpoch {epoch}')
            
            loss_train_avg = loss_train_total/len(dataloader_train)            
            tqdm.write(f'Training loss: {loss_train_avg}')
            
            if test_df is not None:
                val_loss, predictions, true_vals = self.evaluate(dataloader_validation)
                val_f1, val_acc, val_precision, val_recall = self.get_metric(predictions, true_vals)
                tqdm.write(
                    f'Validation Loss: {val_loss} \n'
                    f'- F1-score: {val_f1} - Accuracy: {val_acc} \n'
                    f'- Precision: {val_precision} - Recall: {val_recall}'
                )
                
                # self.accuracy_per_class(predictions, true_vals)
                report = self.report_func(predictions, true_vals)
                pprint(report)
                print('\n', self.label_dict, '\n')

                if val_acc > BEST_METRIC:
                    BEST_METRIC = val_acc

                    print(f'SAVE BEST MODEL at epoch {epoch} \n')
                    torch.save({
                        'model_state_dict': self.model.state_dict(), 
                        'optimizer_state_dict': self.optimizer.state_dict(), 
                        'label_dict': self.label_dict, 
                        'best_metric': BEST_METRIC,
                        # 'epoch': epoch, 
                        'loss': loss_train_avg
                        
                    }, f'models/{name}.model')

                print(f"\n- Path to the saved model: './models/{name}.model'")

            else:
                print(f'SAVE BEST MODEL at epoch {epoch} \n')
                torch.save({
                    'model_state_dict': self.model.state_dict(), 
                    'optimizer_state_dict': self.optimizer.state_dict(), 
                    'label_dict': self.label_dict, 
                    'best_metric': self.BEST_METRIC,
                    # 'epoch': epoch, 
                    'loss': loss_train_avg
                    
                }, f'models/{name}_{epoch}.model')

                print(f"\n- Path to the saved model: './models/{name}_{epoch}.model'")


    def fine_tuning(
        self, 
        model_path: Text=None, 
        data_path: Text=None, 
        text_col: Text='text', 
        label_col: Text='label', 
        bs: int=32, 
        lr: float=1e-5, 
        eps: float=1e-8, 
        epochs: int=10,
        is_normalize: bool=False, 
        name: str='best_model', 
        **kwargs 
    ):

        """Fine-tuning a Classifier model

        :param model_path: Path to the pretrained model
        :param data_path: Path to the data (.csv format) to fine-tuning
        :param text_col: The column name of text field
        :param label_col: The column name of label field
        :param bs: Batch size (default: 32)
        :param lr: Learning rate (default: 1e-5)
        :param eps: Epsilon (default: 1e-8)
        :param epochs: The number of epochs training (default: 10)
        :param is_normalize: If True nornamlize data (default: True)
        :param name: The name file to save model (default: best_model)

        """

        self.load(path=model_path)
        self.model.to(self.device)

        ## PRE-PROCESSING DATA
        train_df = None
        if data_path:
            train_df = pd.read_csv(data_path, encoding='utf-8')
            if not text_col in train_df.columns:
                train_df = fill_text(train_df)
            if is_normalize:
                train_df = normalize_df(
                    train_df, col=text_col, rm_url=True, rm_emoji=True, rm_special_characters=True)
        else:
            raise ValueError(f"'train_path' must be not None values ! ")
        
            
        if train_df is not None:
            train_df[label_col] = train_df[label_col].replace(self.label_dict)            
            encoded_data_train = self.tokenizer.batch_encode_plus(
                train_df[text_col].values, 
                add_special_tokens=True, 
                return_attention_mask=True, 
                pad_to_max_length=True, 
                max_length=256, 
                return_tensors='pt', 
                truncation=True
            )

            input_ids_train = encoded_data_train['input_ids']
            attention_masks_train = encoded_data_train['attention_mask']
            labels_train = torch.tensor(train_df[label_col].values)
            dataset_train = TensorDataset(input_ids_train, attention_masks_train, labels_train)

            print(f"\n- Length of Train set={len(dataset_train)}")

            dataloader_train = DataLoader(
                dataset_train, 
                sampler=RandomSampler(dataset_train), 
                batch_size=bs
            )

        print(f"\n- The current best_metric: {self.BEST_METRIC}")
        print(f"\n- START FINE-TUNING MODEL...\n")

        self.optimizer = AdamW(self.model.parameters(), lr=lr, eps=eps)
        # self.optimizer.load_state_dict(self.checkpoint['optimizer_state_dict'])
        self.scheduler = get_linear_schedule_with_warmup(self.optimizer, num_warmup_steps=0, num_training_steps=len(dataloader_train)*epochs)

        for epoch in tqdm(range(1, epochs+1)):
            self.model.train()
            
            loss_train_total = 0

            progress_bar = tqdm(dataloader_train, desc='Epoch {:1d}'.format(epoch), leave=False, disable=False)
            for batch in progress_bar:

                self.model.zero_grad()
                
                batch = tuple(b.to(self.device) for b in batch)
                
                inputs = {
                    'input_ids':      batch[0],
                    'attention_mask': batch[1],
                    'labels':         batch[2],
                }       

                outputs = self.model(**inputs)
                
                loss = outputs[0]
                loss_train_total += loss.item()
                loss.backward()

                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)

                self.optimizer.step()
                self.scheduler.step()
                
                progress_bar.set_postfix({'training_loss': '{:.3f}'.format(loss.item()/len(batch))})
                
            if not os.path.exists('models/'):
                os.mkdir('models/')
                
            tqdm.write(f'\nEpoch {epoch}')
            
            loss_train_avg = loss_train_total/len(dataloader_train)            
            tqdm.write(f'Training loss: {loss_train_avg}')

            print(f"SAVE MODEL at epoch {epoch}")
            torch.save({
                'model_state_dict': self.model.state_dict(), 
                'optimizer_state_dict': self.optimizer.state_dict(), 
                'label_dict': self.label_dict, 
                'best_metric': self.BEST_METRIC,
                # 'epoch': epoch, 
                'loss': loss_train_avg
                
            }, f'models/{name}_{epoch}.model')

            print(f"\n- Path to the saved model: './models/{name}_{epoch}.model'")

    def get_metric(self, preds, labels):
        """Function to get metrics evaluation
    
        :param preds: Ground truth (correct) target values
        :param labels: Estimated targets as returned by a classifier
        
        :returns: acc, f1, precision, recall metrics.
        """
        preds_flat = np.argmax(preds, axis=1).flatten()
        labels_flat = labels.flatten()

        f1 = f1_score(labels_flat, preds_flat, average='weighted')
        acc = accuracy_score(labels_flat, preds_flat)
        precision = precision_score(labels_flat, preds_flat, average='weighted')
        recall = recall_score(labels_flat, preds_flat, average='weighted')

        return f1, acc, precision, recall
    
    def report_func(self, preds, labels):
        """Function to build a text report showing the main classification metrics.

        :param preds: Estimated targets as returned by a classifier
        :param labels: Ground truth (correct) target values

        :returns: Text summary of the precision, recall, F1 score for each class. \n
                  Dictionary returned if output_dict is True. Dictionary has the following structure: \n
                  \n
                    {'label 1': { \n 
                                'precision':0.5, \n
                                'recall':1.0, \n
                                'f1-score':0.67, \n
                                'support':1 \n
                            }, \n
                    'label 2': { ... }, \n
                    ... \n
                    } \n

        """
        preds_flat = np.argmax(preds, axis=1).flatten()
        labels_flat = labels.flatten()

        return classification_report(y_pred=preds_flat, y_true=labels_flat)
        
    def evaluate(self, dataloader_val):
        """Function to evaluate the Classifier model

        :param dataloader_val: A DataLoader in pytorch for valid/test dataset
        
        """

        self.model.eval()
        
        loss_val_total = 0
        predictions, true_vals = [], []
        
        for batch in dataloader_val:
            
            batch = tuple(b.to(self.device) for b in batch)
            
            inputs = {
                'input_ids':      batch[0], 
                'attention_mask': batch[1], 
                'labels':         batch[2],
            }

            with torch.no_grad():        
                outputs = self.model(**inputs)
                
            loss = outputs[0]
            logits = outputs[1]
            loss_val_total += loss.item()

            logits = logits.detach().cpu().numpy()
            label_ids = inputs['labels'].cpu().numpy()
            predictions.append(logits)
            true_vals.append(label_ids)
        
        loss_val_avg = loss_val_total/len(dataloader_val) 
        
        predictions = np.concatenate(predictions, axis=0)
        true_vals = np.concatenate(true_vals, axis=0)
                
        return loss_val_avg, predictions, true_vals

    def load(self, path):
        """Function to load the pretrained Classifier model

        :param path: (str) Path to the pretrained Classifier model

        """
        path = os.path.abspath(path)
        self.checkpoint = torch.load(path)
        self.label_dict = self.checkpoint['label_dict']

        self.model = AutoModelForSequenceClassification.from_pretrained(self.pretrained, 
                                                            num_labels=len(self.label_dict), 
                                                            output_attentions=False, 
                                                            output_hidden_states=False)

        self.model.load_state_dict(self.checkpoint['model_state_dict'])
        self.BEST_METRIC = self.checkpoint['best_metric']
        # self.loss = checkpoint['loss']
        # self.epoch = checkpoint['epoch']
        
    
    def predict(self, sample: Text, is_normalize: bool=True):
        """Function to inference a given samples

        :param sample: (Text) The sample to inference
        :param is_normalize: (bool) If True normalize sample before predict (default: True)

        :returns: The results format: \n
                    { \n
                        'class': 'macro_news', \n
                        'score': 0.9999, \n
                    } \n

        """
        if not self.model:
            raise ValueError(f"The model_path is None or invalid.")

        label_dict_inverse = {v: k for k, v in self.label_dict.items()}

        self.model.eval()
        if is_normalize:
            sample = normalize(
                text=sample, rm_emoji=True, rm_url=True, 
                rm_special_characters=True, lowercase=True)

        if len(sample.split()) > 240:
            sample = ' '.join(sample.split()[:240])
                
        input = self.tokenizer.encode_plus(sample, return_tensors='pt')
        prediction = self.model(**input)[0]
        score = torch.nn.functional.softmax(prediction).detach().numpy()
        max_index = np.argmax(score)
        
        return {
            'class': label_dict_inverse[max_index], 
            'score': score[0][max_index]
        }
