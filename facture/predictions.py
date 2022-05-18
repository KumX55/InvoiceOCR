import numpy as np
import pandas as pd
import cv2
import pytesseract
from glob import glob
import spacy
import re
import string
from spacy import displacy
import warnings
warnings.filterwarnings('ignore')
# loading nlp model
model_ner = spacy.load('/home/kumx55/Desktop/OCR-PFE/OCR-DJANGO/output/model-best/')

def cleanText(txt):
    whitespace = string.whitespace
    punctuation = '!#$&\'()*+:;<=>?[\\]^`{|}~'
    tableWhitespace = str.maketrans('','',whitespace)
    tablePuntuation = str.maketrans('','',punctuation)
    text = str(txt)
    text = text.lower()
    removewhispace = text.translate(tableWhitespace)
    removepunctuation = removewhispace.translate(tablePuntuation)
    return str(removepunctuation)

# group labels
class groupgen():
    def __init__(self):
        self.id = 0
        self.text = ''
    def getgroup(self,text):
        if self.text == text:
            return self.id
        else:
            self.id +=1
            self.text = text
            return self.id

# # Parser
def parser(text,label):
    if label in ('FPHONE','CPHONE'):
        text = text.lower()
        text = re.sub(r'\D','',text)
    elif label in ('FMAIL','CMAIL','CADD','FADD'):
        text = text.lower()
        allow_special_chart = '@_.\-'
        text = re.sub(r'[^A-Za-z0-9{} ]'.format(allow_special_chart),'',text)
    elif label == 'WEB':
        text = text.lower()
        allow_special_chart = ':/.%#-?'
        text = re.sub(r'[^A-Za-z0-9{} ]'.format(allow_special_chart),'',text)
    elif label in ('CNAME','FNAME','PNAME','DES'):
        text = text.lower()
        text = re.sub(r'[^a-z ]','',text)
        text = text.title()
    elif label == 'ISTATUS':
        text = text.lower()
        text = re.sub(r'[^a-z ]','',text)
        text = text.title()
    return text

grp_gen = groupgen()
# Load Image
def prediction(image):
    # Extract data using pyteserract
    tessData = pytesseract.image_to_data(image)
    tessData
    # convert data into dataframe
    tesslist = list(map(lambda x:x.split('\t'),tessData.split('\n')))
    df = pd.DataFrame(tesslist[1:],columns=tesslist[0])
    df.dropna(inplace=True) # drop missing values
    df['text'] = df['text'].apply(cleanText)
    # convert data into content
    df_clean = df.query("text != '' ")
    content = " ".join([w for w in df_clean['text']])
    # get predictions from NER model
    doc = model_ner(content)


    #displacy.serve(doc,style='ent')
    #displacy.render(doc,style='ent')


    # # Tagging

    #converting doc in json
    docjson = doc.to_json()
    docjson.keys()


    doc_text = docjson['text']

    # creating tokens
    dataframe_tokens = pd.DataFrame(docjson['tokens'])
    dataframe_tokens['token'] = dataframe_tokens[['start','end']].apply(lambda x:doc_text[x[0]:x[1]] , axis=1)
    dataframe_tokens.head(10)

    right_table = pd.DataFrame(docjson['ents'])[['start','label']]
    dataframe_tokens = pd.merge(dataframe_tokens, right_table, how='left',on='start')

    dataframe_tokens.fillna('O',inplace=True)
    dataframe_tokens.head(10)

    # join label to df_clean dataframe
    df_clean['end'] =  df_clean['text'].apply(lambda x: len(x)+1).cumsum() - 1
    df_clean['start'] = df_clean[['text','end']].apply(lambda x: x[1] - len(x[0]), axis=1 )

    # inner join with start 
    dataframe_info = pd.merge(df_clean,dataframe_tokens[['start','token','label']],how='inner',on='start')
    dataframe_info.tail(10)

    # # Bounding Box

    bb_df = dataframe_info.query("label != 'O' ")

    bb_df['label'] = bb_df['label'].apply(lambda x: x[2:])
    bb_df['group'] = bb_df['label'].apply(grp_gen.getgroup)

    # right and bottom of bounding box
    bb_df[['left','top','width','height']] = bb_df[['left','top','width','height']].astype(int)
    bb_df['right'] = bb_df['left'] + bb_df['width']
    bb_df['bottom'] = bb_df['top'] + bb_df['height']

    # tagging: groupby group
    col_group = ['left','top','right','bottom','label','token','group']
    group_tag_img = bb_df[col_group].groupby(by='group')
    img_tagging = group_tag_img.agg({
        
        'left':min,
        'right':max,
        'top':min,
        'bottom':max,
        'label':np.unique,
        'token':lambda x: " ".join(x)
        
    })

    # img_bb = image.copy()
    # for l,r,t,b,label,token in img_tagging.values:
    #     cv2.rectangle(img_bb,(l,t),(r,b),(0,255,0),2)
    #     cv2.putText(img_bb,label,(l,t),cv2.FONT_HERSHEY_PLAIN,1,(255,0,255),2)
        
    #parser('Srikanth^$#&)@gmail.com','EMAIL')

    # # Entities

    info_array = dataframe_info[['token','label']].values
    entities = dict(FNAME=[],FADD=[],FMAIL=[],FPHONE=[],CNAME=[],CADD=[],CMAIL=[],CPHONE=[],PNAME=[],PQTY=[],PTVA=[],PPUHT=[],PMONT=[],PTTC=[],IREF=[],IDATE=[],IMHT=[],ITOTAL=[],ISTATUS=[])
    previous = 'O'
    for token, label in info_array:
        bio_tag = label[0]
        label_tag = label[2:]
        
        # step -1 parse the token
        text = parser(token,label_tag)
        
        if bio_tag in ('B','I'):
            
            if previous != label_tag:
                entities[label_tag].append(text)
                
            else:
                if bio_tag == "B":
                    entities[label_tag].append(text)
                    
                else:
                    if label_tag in ('FNAME','FADD','FMAIL','FPHONE','CNAME','CADD','CMAIL','CPHONE','PNAME','PQTY','PTVA','PPUHT','PMONT','PTTC','IREF','IDATE','IMHT','ITOTAL','ISTATUS'):
                        entities[label_tag][-1] = entities[label_tag][-1] + " " + text
                        
                    else:
                        entities[label_tag][-1] = entities[label_tag][-1] + text
                        
        
        
        previous = label_tag



    return entities







