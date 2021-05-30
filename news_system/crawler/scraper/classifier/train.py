#!/home/ubuntu/anaconda3/envs/ainews/bin/python
# -*- coding: utf-8 -*-

import os
import time
import argparse

from classifier import Classifier
from utils import normalize


	
if __name__=='__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument("--train_path", type=str, required=True, 
                        help="The path to training data")
    parser.add_argument("--test_path", type=str, default=None, 
                        help="The path to test data")
    parser.add_argument("--text_col", type=str, default='text', 
                        help="The column name of text field")
    parser.add_argument("--label_col", type=str, default='category', 
                        help="The column name of label field")
    parser.add_argument("--epochs", type=int, default=15, 
                        help="Number of epochs to train the model")
    parser.add_argument("--bs", type=int, default=32, 
                        help="The batch size value")
    parser.add_argument("--lr", type=float, default=1e-5, 
                        help="Leaning rate")
    parser.add_argument("--from-pretrained", type=str, default="None",
                        help="The file name to save model")
    parser.add_argument("--is_normalize", type=bool, default=True, 
                        help="If True, normalize data before training the model")
    parser.add_argument("--name", type=str, default="best_model",
                        help="The file name to save model")

    args = parser.parse_args()


    ## Training the model

    print(f"\n- START TRAINING MODEL ...\n") 

    classifier = Classifier(pretrained="vinai/phobert-base")
    if args.from_pretrained is "None":
        classifier.train(
            train_path=args.train_path,
            test_path=args.test_path,
            text_col=args.text_col,
            label_col=args.label_col,
            bs=args.bs,
            epochs=args.epochs,  ## epochs=5
            lr=args.lr,
            is_normalize=args.is_normalize,
            name=args.name
        )
    else:
        classifier.fine_tuning(
            model_path=args.from_pretrained,
            train_path=args.train_path,
            test_path=args.test_path,
            text_col=args.text_col,
            label_col=args.label_col,
            bs=args.bs,
            epochs=args.epochs,  ## epochs=5
            lr=args.lr,
            is_normalize=args.is_normalize,
            name=args.name
        )

    print(f"\nEND !\n")