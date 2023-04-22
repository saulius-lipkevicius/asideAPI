import json
import requests
from cosSimilarity import *

"""
with open('hackaton.json', 'r') as f:
    # Load the contents of the file into a dictionary
    data = json.load(f)
"""

def process_input(data):

    # get all authors
    all_authors_list = []
    for info in data['data']:
        try:
            if info['authors'][0]['name'] is not None and info['abstract'] is not None:
                all_authors_list.append(info['authors'][0]['authorId'])
        except:
            pass



    # request author data
    req = requests.post(
        'https://api.semanticscholar.org/graph/v1/author/batch',
        params={'fields': 'paperCount,affiliations,hIndex,citationCount'},
        json={"ids":all_authors_list}
    )

    author_metadata = req.json()

    # get information to normalize parameters
    countCitation_list = []
    avgCitation_list = []
    hIndex_list = []
    paperCount_list = []

    for info in author_metadata:
        countCitation_list.append(info['citationCount'])
        avgCitation_list.append(info['citationCount'] / info['paperCount'])
        hIndex_list.append(info['hIndex'])
        paperCount_list.append(info['paperCount'])

    ## find exact normalization parameters
    countCitation_min, countCitation_max = min(countCitation_list), max(countCitation_list)
    avgCitation_list_min, avgCitation_list_max = min(avgCitation_list), max(avgCitation_list)
    hIndex_list_min, hIndex_list_max = min(hIndex_list), max(hIndex_list)
    paperCount_list_min, paperCount_list_max = min(paperCount_list), max(paperCount_list)


    # fill
    final_list = []
    i = 0
    for item in data['data']:
        try:
            if item['authors'][0]['name'] is not None and item['abstract'] is not None:
                row_data = {}
                row_data['authorName'] = item['authors'][0]['name']
                row_data['authorId'] = item['authors'][0]['authorId']
                row_data['title'] = item['title']
                row_data['abstract'] = item['abstract']
                row_data['paperId'] = item['paperId']

                row_data['countCitation'] = (author_metadata[i]['citationCount'] - countCitation_min) / countCitation_max
                row_data['hIndex'] = (author_metadata[i]['hIndex'] - hIndex_list_min) / hIndex_list_max
                row_data['paperCount'] = (author_metadata[i]['paperCount'] - paperCount_list_min) / paperCount_list_max
                row_data['avgCitation'] = ((row_data['countCitation'] / row_data['paperCount']) ) / avgCitation_list_max

                row_data['measure'] = (row_data['countCitation'] + row_data['hIndex'] + row_data['paperCount'] + row_data['avgCitation']) / 4
                final_list.append(row_data)
        except:
            pass
        i+=1

    abstract_list = []
    for paper in final_list:
        abstract_list.append(paper['abstract'])

    # run similarity measure


    for main_abstract in final_list:
        for comparing_abstract in final_list:
            simMeasure = 0
            try:
                vector1 = text_to_vector(main_abstract['abstract'])
                vector2 = text_to_vector(comparing_abstract['abstract'])

                cosine = get_cosine(vector1, vector2)

                simMeasure += cosine
            except:
                    pass
        main_abstract['cosSimilarity'] = simMeasure / len(final_list)

        
    # Save final json
    json_object = json.dumps(final_list) # Serializing json  
    #with open("sample.json", "w") as outfile:
    #    json.dump(json_object, outfile)
    return json_object