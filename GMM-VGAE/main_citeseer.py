#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Authors : Nairouz Mrabah (mrabah.nairouz@courrier.uqam.ca) & Mohamed Fawzi Touati (touati.mohamed_fawzi@courrier.uqam.ca)
# @Paper   : Rethinking Graph Autoencoder Models for Attributed Graph Clustering
# @License : MIT License

import numpy as np
import torch
import scipy.sparse as sp
import itertools
from model import GMM_VGAE
from datasets import format_data
from preprocessing import load_data, sparse_to_tuple, preprocess_graph


# Dataset Name
dataset = "Citeseer"
print("Citeseer dataset")
feas = format_data('citeseer', './data/Citeseer')
num_nodes = feas['features'].size(0)
num_features = feas['features'].size(1)
nClusters = 6
adj, features , labels = load_data('citeseer', './data/Citeseer')

# Network parameters
num_neurons = 32
embedding_size = 16
save_path = "./results/"

# Pretraining parameters
epochs_pretrain = 200
lr_pretrain = 0.01

# Clustering parameters
epochs_cluster = 200
lr_cluster = 0.01


# Data processing 
adj = adj - sp.dia_matrix((adj.diagonal()[np.newaxis, :], [0]), shape=adj.shape)
adj.eliminate_zeros()
adj_norm = preprocess_graph(adj)
features = sparse_to_tuple(features.tocoo())
num_features = features[2][1]
pos_weight_orig = float(adj.shape[0] * adj.shape[0] - adj.sum()) / adj.sum()
norm = adj.shape[0] * adj.shape[0] / float((adj.shape[0] * adj.shape[0] - adj.sum()) * 2)
adj_label = adj + sp.eye(adj.shape[0])
adj_label = sparse_to_tuple(adj_label)
adj_norm = torch.sparse.FloatTensor(torch.LongTensor(adj_norm[0].T), torch.FloatTensor(adj_norm[1]), torch.Size(adj_norm[2]))
adj_label = torch.sparse.FloatTensor(torch.LongTensor(adj_label[0].T), torch.FloatTensor(adj_label[1]), torch.Size(adj_label[2]))
features = torch.sparse.FloatTensor(torch.LongTensor(features[0].T), torch.FloatTensor(features[1]), torch.Size(features[2]))
weight_mask_orig = adj_label.to_dense().view(-1) == 1
weight_tensor_orig = torch.ones(weight_mask_orig.size(0))
weight_tensor_orig[weight_mask_orig] = pos_weight_orig

# Training
acc_array = []
network = GMM_VGAE(adj = adj_norm , num_neurons=num_neurons, num_features=num_features, embedding_size=embedding_size, nClusters=nClusters, activation="ReLU")
#acc_array = network.pretrain(adj_norm, features, adj_label, labels, weight_tensor_orig, norm, optimizer="Adam", epochs=epochs_pretrain, lr=lr_pretrain, save_path=save_path, dataset=dataset)
acc_array, y_pred, y = network.train(acc_array, adj_norm, features, adj_label, labels, weight_tensor_orig, norm, optimizer="Adam", epochs=epochs_cluster, lr=lr_cluster, save_path=save_path, dataset=dataset)