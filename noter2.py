import argparse
from multiprocessing import Pool #multiproccsing tool
import numpy as np
import copy
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import igraph as ig
import json
import chart_studio.plotly as py
from plotly.offline import iplot
import plotly.graph_objs as go
#setting functions

def remove_specificSymbols_fromLine(line_vector):
    new_line_vector = []
    for word in line_vector:
        new_word = ''.join(char for char in word if char.isalnum())
        new_line_vector.append(new_word)
    return new_line_vector
#get stopwords
"""
    stopwords are from https://www.ranks.nl/stopwords
"""

def init_files():
    f = open("/data/stopwords.txt", "r")
    raw_stopwords = f.read()
    f.close()
    stopwords = raw_stopwords.split()

    # Manually adding terminate words for speech to text
    stopwords.append("quit")
    stopwords.append("exit")
    stopwords.append(" ")
    stopwords.append("i")


    # get text file to analyze through argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("written_file")
    args = parser.parse_args()


    file = open(args.written_file, "r")
    raw_file = file.read()
    file.close()

    return stopwords, raw_file

"""
    make_text is for making words matrix which is easy to analyze.
    Following actions are inside the function.
    1. Remove general unnecessities
        ',' ,  ' ', ''

    2. Remove stopwords using multiprocessing
"""

def make_text(stopwords, raw_file):
    text_splitted_by_line = raw_file.split(".") #splitted by lines

    text = []
    for line in text_splitted_by_line:
        text.append(line.split(" ")) # splitted by words

    for i in range(len(text)):
        for j in range(len(text[i])):
            text[i][j] = text[i][j].lower() # chnage al words to lowercases
            if "," in text[i][j]:
                text[i][j] = text[i][j].replace(",", "") #remove ","




    #Remove stopwords

    for stop_word in stopwords:
        for i in range(len(text)):
            text[i] = [a for a in text[i] if a != stop_word]




    # remove specific symbols using multiproccsing
    p = Pool(4)
    text = p.map(remove_specificSymbols_fromLine, text)

    for i in range(len(text)):
        text[i] = [a for a in text[i] if a != ''] #remove null value
    text = [a for a in text if a != []]          #remove null lines

    return text

def make_tfidf_cooccurrence(text_vector):
    """
        firstly making a list of words without duplications
    """
    word_list = []
    for line in text_vector:
        for word in line:
            if word not in word_list:
                word_list.append(word)

    """
        secondly making a matrix which shows
            - frequencies that a word appears in a line : TF_vector
            - how many lines a word is included in      : IDF_vector

            -> how important a word is in each line     : TFIDF_vector
    """
    text_word_vector = np.zeros((len(text_vector),len(word_list)))
    text_word_vector_forCooccurrence = np.zeros((len(text_vector),len(word_list)))
    number_of_lines_including_a_word = np.zeros(len(word_list))
    for i in range(len(text_vector)):
        for j in range(len(word_list)):
            text_word_vector[i,j] = text_vector[i].count(word_list[j])
            if word_list[j] in text_vector[i]:
                number_of_lines_including_a_word[j] += 1
                text_word_vector_forCooccurrence[i,j] = 1
    number_of_words_for_each_words = text_word_vector.sum(axis=0)

    TF_vector = text_word_vector/number_of_words_for_each_words
    IDF_vector = np.log(len(text_vector)/number_of_lines_including_a_word) + 1
    TFIDF_vector = TF_vector * IDF_vector

    """
        calculation of co-occurrence matrix
    """
    cooccurrence_matrix = np.dot(text_word_vector_forCooccurrence.T, text_word_vector_forCooccurrence)

    return word_list,TFIDF_vector, cooccurrence_matrix

"""
    picking up sets of top n words which are most important in each line
"""
def importance_of_words(TFIDF_vector, word_list,top_n):
    """
        giving 2 lists
            - top n keywords for each sentences
            - top 10 words which can be supposed to be most important
    """
    results = []
    results_withTFIDF = []
    for i in range(TFIDF_vector.shape[0]):
        line = TFIDF_vector[i].copy()
        words = copy.copy(word_list)
        sub_results = []
        sub_results_TFIDF = []
        for j in range(top_n):
            n = np.argmax(line)
            sub_results.append(words[n])
            sub_results_TFIDF.append(line[n])
            line = np.delete(line,n)
            words = np.delete(words,n)
        results.append(sub_results)
        results_withTFIDF.append(sub_results_TFIDF)

    results_withTFIDF = np.array(results_withTFIDF)
    return results, results_withTFIDF

def make_nodes_weigh(word_list,cooccurrence_matrix):
    results = []
    for i in range(len(word_list)):
        for j in range(i+1, len(word_list)):
            if (cooccurrence_matrix[i,j]!=0):
                results.append([word_list[i], word_list[j], cooccurrence_matrix[i,j]])

    with open("nodes_for_processing.txt", "w") as f:
        for i in range(len(word_list)):
            f.write("{},{},{}\n".format(results[i][0], results[i][1], results[i][2]))
    return results

def make_graph_data(network_data, word_list):
    """
        1. check if there are some words which didn't occurr with any other words and delete it.
    """
    copied_wordList = word_list
    for word in copied_wordList:
        flag = False
        for i in range(len(network_data)):
            if (word == network_data[i][0]) or (word == network_data[i][1]):
                flag = True
        if flag == False:
            copied_wordList.remove(word)
    G = nx.Graph()
    for i in range(len(copied_wordList)):
        G.add_node(i, name=copied_wordList[i])
    for i in range(len(network_data)):
        G.add_edge(word_list.index(network_data[i][0]),word_list.index(network_data[i][1]), weight=network_data[i][2])
    return G

def make_graph_dict(graph):
    igraph_dict = {'nodes':[{'name':graph.nodes[k]['name'], 'group':1} for k in range(len(graph.nodes))], 'links':[{'source':list(graph.edges)[k][0], 'target':list(graph.edges)[k][1], 'value':list(graph.edges.data())[k][2]['weight']} for k in range(len(graph.edges))]}
    return igraph_dict

if __name__ == '__main__':
    stopwords, raw_file = init_files()
    bag_of_words = make_text(stopwords, raw_file)
    print(len(bag_of_words))
    word_list,TFIDF,cooccur = make_tfidf_cooccurrence(bag_of_words)
    importance, importance_tfidf = importance_of_words(TFIDF,word_list,3)
    nodes = make_nodes_weigh(word_list, cooccur)

    Graph = make_graph_data(nodes, word_list)
    #print(Graph.edges.data())

    dict = make_graph_dict(Graph)
    print(type(dict))
    #print(dict)
    data = dict

    with open("data.json", "w") as f:
        json.dump(data, f)
