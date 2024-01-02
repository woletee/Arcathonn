@@ -1,380 +1 @@
# -*- coding: utf-8 -*-
"""Untitled51.ipynb

Automatically generated by Colaboratory.
Original file is located at
    https://colab.research.google.com/drive/1S_irLVWW884_WcZ0MU4MZlPx_G_WZ4EY
"""

import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import json
from pathlib import Path
from collections import defaultdict
from itertools import product
from matplotlib import colors
import matplotlib.pyplot as plt
import numpy as np
from itertools import combinations,permutations
from sklearn.tree import *
from sklearn import tree
from sklearn.ensemble import BaggingClassifier
import random
from math import floor
from pathlib import Path
import zipfile
import os

# Path to the ZIP files
test_zip_path = Path('test.zip')
training_zip_path = Path('training.zip')
evaluation_zip_path = Path('evaluation.zip')

# Extract the ZIP files
with zipfile.ZipFile(test_zip_path, 'r') as test_zip:
    test_zip.extractall('test')  # Extracts files to 'test' directory

with zipfile.ZipFile(training_zip_path, 'r') as training_zip:
    training_zip.extractall('training')  # Extracts files to 'training' directory

with zipfile.ZipFile(evaluation_zip_path, 'r') as evaluation_zip:
    evaluation_zip.extractall('evaluation')  # Extracts files to 'evaluation' directory

training_path = Path('training/training')
test_path = Path('test')
evaluation_path = Path('evaluation/evaluation')
# Load the file directories into variables
training_tasks = sorted(os.listdir(training_path))
test_tasks = sorted(os.listdir(test_path))
evaluation_tasks = sorted(os.listdir(evaluation_path))

#the plot_result function plots the specific task input(inp), its test expected output(eoup), and model's prediction(oup) . it uses matplotlib for plotting.
def plot_result(inp,eoup,oup):
    """
    Plots the first train and test pairs of a specified task,
    using same color scheme as the ARC app
    """
    cmap = colors.ListedColormap(
        ['#000000', '#0074D9','#FF4136','#2ECC40','#FFDC00',
         '#AAAAAA', '#F012BE', '#FF851B', '#7FDBFF', '#870C25'])
    norm = colors.Normalize(vmin=0, vmax=9)
    fig, axs = plt.subplots(1, 3, figsize=(15,15))

    axs[0].imshow(inp, cmap=cmap, norm=norm)
    axs[0].axis('off')
    axs[0].set_title('Input')

    axs[1].imshow(eoup, cmap=cmap, norm=norm)
    axs[1].axis('off')
    axs[1].set_title('Output')

    axs[2].imshow(oup, cmap=cmap, norm=norm)
    axs[2].axis('off')
    axs[2].set_title('Model prediction')

    plt.grid()
    plt.tight_layout()
    plt.show()
#the plot_maths function is a general purpose matric for visualizing a lsit of matrices 
def plot_mats(mats):
    cmap = colors.ListedColormap(
        ['#000000', '#0074D9','#FF4136','#2ECC40','#FFDC00',
         '#AAAAAA', '#F012BE', '#FF851B', '#7FDBFF', '#870C25'])
    norm = colors.Normalize(vmin=0, vmax=9)
    fig, axs = plt.subplots(1, len(mats), figsize=(15,15))

    for i in range(len(mats)):
        axs[i].imshow(mats[i], cmap=cmap, norm=norm)
        axs[i].axis('off')
        axs[i].set_title('Fig: '+str(i))

    plt.rc('grid', linestyle="-", color='white')
    plt.grid(True)
    plt.tight_layout()
    plt.show()
#the getioric function takes in a specific task as input and then extracts its input and output matrics and then return them along with the dimension of the task(column and row)
def getiorc(pair):
    inp = pair["input"]
    return pair["input"],pair["output"],len(inp),len(inp[0])
#the getAround function is used to return the values of neighbouring elements around a given position i and j
def getAround(i,j,inp,size=1):
    #v = [-1,-1,-1,-1,-1,-1,-1,-1,-1]
    r,c = len(inp),len(inp[0])
    v = []
    sc = [0]
    for q in range(size):
        sc.append(q+1)
        sc.append(-(q+1))
    for idx,(x,y) in enumerate(product(sc,sc)):
        ii = (i+x)
        jj = (j+y)
        v.append(-1)
        if((0<= ii < r) and (0<= jj < c)):
            v[idx] = (inp[ii][jj])
    return v
#this getDiagonal function is actually like a place holder that can be used for later operations
def getDiagonal(i,j,r,c):
    return
#the getx function extracts important features for a given position i and j in a 2D matrix





#the get_flips function retruns a list of tuples where each tuple contains matrics that came as a result of flip rotations 
def get_flips(inp,oup):
    result = [] #store generated matrics
    n_inp = np.array(inp)
    n_oup = np.array(oup)
    result.append((np.fliplr(inp).tolist(),np.fliplr(oup).tolist())) #flipping both the input and the output horizontally 
    result.append((np.rot90(np.fliplr(inp),1).tolist(),np.rot90(np.fliplr(oup),1).tolist()))#flipping horizontally and then rotating 90 degrees 
    result.append((np.rot90(np.fliplr(inp),2).tolist(),np.rot90(np.fliplr(oup),2).tolist()))#flipping horizontally and then rotating 180 degrees 
    result.append((np.rot90(np.fliplr(inp),3).tolist(),np.rot90(np.fliplr(oup),3).tolist()))#flipping horizontally and then rotating 270 degrees 
    result.append((np.flipud(inp).tolist(),np.flipud(oup).tolist()))#flipping vertically both the input and the output 
    return result

def gettaskxy(task_json,aug,around_size,bl_cols,flip=True):
    X = []
    Y = []
    for pair in task_json['train']:
        inp,oup=pair["input"],pair["output"]
        tx,ty = getXy(inp,oup,around_size)
        X.extend(tx)
        Y.extend(ty)
        if(flip):
            for ainp,aoup in get_flips(inp,oup):
                tx,ty = getXy(ainp,aoup,around_size)
                X.extend(tx)
                Y.extend(ty)
                if(aug):
                    augs = augment(ainp,aoup,bl_cols)
                    for ainp,aoup in augs:
                        tx,ty = getXy(ainp,aoup,around_size)
                        X.extend(tx)
                        Y.extend(ty)
        if(aug):
            augs = augment(inp,oup,bl_cols)
            for ainp,aoup in augs:
                tx,ty = getXy(ainp,aoup,around_size)
                X.extend(tx)
                Y.extend(ty)
    return X,Y

def test_predict(task_json,model,size):
    inp = task_json['test'][0]['input']
    eoup = task_json['test'][0]['output']
    r,c = len(inp),len(inp[0])
    oup = predict(inp,model,size)
    return inp,eoup,oup


def submit_predict(task_json,model,size):
    pred_map = {}
    idx=0
    for pair in task_json['test']:
        inp = pair["input"]
        oup = predict(inp,model,size)
        pred_map[idx] = oup.tolist()
        idx+=1
        plot_result(inp,oup,oup)
    return pred_map
e(task_json):
    return 4;

def get_bl_cols(task_json):
    result = []
    bkg_col = getBkgColor(task_json);
    result.append(bkg_col)
     # num_input,input_cnt,num_output,output_cnt
    met_map = {}
    for i in range(10):
        met_map[i] = [0,0,0,0]

    total_ex = 0
    for pair in task_json['train']:
        inp,oup=pair["input"],pair["output"]
        u,uc = np.unique(inp, return_counts=True)
        inp_cnt_map = dict(zip(u,uc))
        u,uc = np.unique(oup, return_counts=True)
        oup_cnt_map = dict(zip(u,uc))

        for col,cnt in inp_cnt_map.items():
            met_map[col][0] = met_map[col][0] + 1
            met_map[col][1] = met_map[col][1] + cnt
        for col,cnt in oup_cnt_map.items():
            met_map[col][2] = met_map[col][2] + 1
            met_map[col][3] = met_map[col][3] + cnt
        total_ex+=1

    for col,met in met_map.items():
       num_input,input_cnt,num_output,output_cnt = met
       if(num_input == total_ex or num_output == total_ex):
            result.append(col)
       elif(num_input == 0 and num_output > 0):
            result.append(col)

    result = np.unique(result).tolist()
    if(len(result) == 10):
        result.append(bkg_col)
    return np.unique(result).tolist()
def flattener(pred):
    str_pred = str([row for row in pred])
    str_pred = str_pred.replace(', ', '')
    str_pred = str_pred.replace('[[', '|')
    str_pred = str_pred.replace('][', '|')
    str_pred = str_pred.replace(']]', '|')
    return str_pred

def combine_preds(tid,pm1,pm3,pm5):
    result = []
    for i in range(len(pm1)):
        tk_s = tid+"_"+str(i)
        str_pred = flattener(pm1[i])+" "+flattener(pm3[i])+" "+flattener(pm5[i])
        #print(tk_s,str_pred)
        result.append([tk_s,str_pred])
    return result
def inp_oup_dim_same(task_json):
    return all([ len(pair["input"]) == len(pair["output"]) and len(pair["input"][0]) == len(pair["output"][0])
                for pair in task_json['train']])


solved_task = 0
total_task = 0
task_ids = []
task_preds = []
for task_path in test_path.glob("*.json"):
    task_json = json.load(open(task_path))
    tk_id = str(task_path).split("/")[-1].split(".")[0]
    print(tk_id)
    if(inp_oup_dim_same(task_json)):
        a_size = get_a_size(task_json)
        bl_cols = get_bl_cols(task_json)

        pred_map_1 = submit_predict(task_json,model_1,1)
        pred_map_3 = submit_predict(task_json,model_3,3)
        pred_map_5 = submit_predict(task_json,model_5,5)

        for tks,str_pred in combine_preds(tk_id,pred_map_1,pred_map_3,pred_map_5):
            task_ids.append(tks)
            task_preds.append(str_pred)
            #print(tks,str_pred)
        solved_task+=1
        #break
    else:
        pred_map_1 = dumb_predict(task_json)
        pred_map_3 = dumb_predict(task_json)
        pred_map_5 = dumb_predict(task_json)
        for tks,str_pred in combine_preds(tk_id,pred_map_1,pred_map_3,pred_map_5):
            task_ids.append(tks)
            task_preds.append(str_pred)
            #print(tks,str_pred)

    total_task+=1
