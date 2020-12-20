# -*- coding: utf-8 -*-
"""
Created on Tue Mar 12 16:21:50 2019

@author: dewandaru@gmail.com

    This is Extended Geoparser code that combines event extractor with the 
    spatial minimality derived disambiguation method.

Requirements:
    geopandas (conda install geopandas)
    sklearn_crfsuite
    gensim
    mpu
    area
    descartes
    GADM all countries data, to be put inside gadm36_shp folder.
    
other required:
    ipostagger.jar inside inanlp package (included)
    jre
    
Instructions:
    - This code was tested under Windows 10 OS, with Spyder IDE
    - Make sure all requirement satisfied by the python interpreter
    - the jre is for inanlp package to run and consulted via OS input/output mechanism
    

    
LOG:
----
    
    we are using train_test_split in this version.
    also improved the is_arg function to analyze how many words matched.
    also this has optimization of the hyperparameter.


    debug_mode = True
    for entity detection:
    
        disable_level
            level 2: disable toponym gazeteer + argument extractor + geofeatures
            level 1: disable toponym gazeteer
            level 0: fully enable all feature
            
    for ploc detection
        
        disable_level
            level 0: fully enable all feature
            level 1: 
        
        
    verbosity
        level 2: very verbose
        level 1: standard
        level 0: performance (no output)
    
    disable_level is replaced with ploc_options, arg_options, and entity_options, and event_options
    
HOW TO:
------
Run this piece of code in ipython or spyder so that no GADM reload are needed.

"""
from itertools import chain
from itertools import product
from shapely.geometry.polygon import Polygon

import sklearn
import scipy.stats
import re
import pickle

from sklearn.metrics import make_scorer
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RandomizedSearchCV
from sklearn.model_selection import train_test_split

import sklearn_crfsuite
from sklearn_crfsuite import scorers
from sklearn_crfsuite import metrics


debug_mode = False
verbosity = 1
dataset_folder = 'train-test-v10'
import semantic_gazetteer
import geospatial_driver
import bio

print("initialize Ina geoparser")
__init__ = True


def is_toponym(w):
    if in_gaz(w):
        #print("LOC ", w)
        return 'T'
    else:
        return 'F'


all_events = topic_peristiwa + event_banjir + event_gempa + event_kebakaran + event_kecelakaan \
+event_banjir_i + event_gempa_i + event_kebakaran_i + event_kecelakaan_i \
+event_longsor + event_hujan + event_hujan_i + event_meeting

def is_geospatial_event(w):
    return inlist(w, all_events)


def avg_labels():
    total = 0
    num = 0
    for i in range(1,450000):
        a = art(i)[0][1]
        try:
            commas = a.count(',')
        except:
            commas = 0
        total = total + commas
        num = num + 1
    print (total/num)

def is_jabatan(w):
    return inlist(w, jabatan)

org_list = [k[0] for k in org_markers]
org_list = sorted(org_list, key = len, reverse=True)
org_arrays = '|'.join(org_list)
p_org_markers = re.compile('('+org_arrays+')(\s('+org_arrays+'))*', re.IGNORECASE) #ignore case for the initial markers
p_org_rest = re.compile('[A-Z]\w+(\s[A-Z]\w+)*')

def is_org(w):
    '''
    returns a number of segment where matching words detect ORG.

    a bit different from is_XXX family, whereby in this function we return number of matches (int)
    the idea is that first portion is case insensitive. for example, "kepala sekolah" , "Kepala Sekolah" etc.
    the rest portion is either camel case or capitals.
    we are using two regex here because python cannot have partially-ignore case and partially case sensitive regex.
    '''
    words = w.split()
    #print (w)
    num_words = 0
    if len(words) > 1: # more than 1 word
        r = p_org_markers.match(w)
        if r: num_words = len(r.group(0).split(' '))
        # print ( num_words )
        if num_words > 0 :

            restwords = words[num_words:]
            rest = ' '.join(restwords)
            r = p_org_rest.match(rest)
            if r:
                return len(r.group(0).split(' ')) + num_words # add 1 because we split into two regex here. 1 is for the first word regex count.
            else:
                return num_words
        else:
            return 0
    else: # 1 word only
        r = p_org_markers.match(words[0]);
        if r:
            return len(r.group(0).split(' '))
        else:
            return 0

p5 = re.compile('pukul\ \d\d\.\d\d\ (wib|wit|wita)?', re.IGNORECASE)
def is_time(w):
    #print("is_time", w)
    return p5.match(w)

p8 = re.compile('[0-2]?[0-9]/[0-1]?[0-9](/\d\d\d\d)?')
def is_date(w):
    return p8.match(w)

p1 = re.compile('(bernomor polisi |bernopol |nopol )?[A-Z]{1,2} [1-9][0-9]{0,3} [A-Z]{2,3}')
def is_nopol(w):
    return p1.match(w)

p6 = re.compile('(RT|RW) ?[0-9]?[0-9]?[0-9](\,\s*?(dan)?\s*[0-9]?[0-9]?[0-9])+', re.IGNORECASE)
def is_rtrw(w):
    return p6.match(w)

kendaraan_list = [k[0] for k in kendaraan]
p13 = re.compile('('+'|'.join(kendaraan_list)+')', re.IGNORECASE)
def is_vehicle(w):
    return p13.match(w)

geovent_list = [k[0] for k in all_events]
geovent_list = sorted(geovent_list, key = len, reverse=True)
p12 = re.compile('('+'|'.join(geovent_list)+')', re.IGNORECASE)
def is_geoevent(w):
    return p12.match(w)

#%%
def configLabels( mode="entity"):
    if mode == "entity":
        return [
            "B-ARG",
            "I-ARG",
            "B-EVE",
            "I-EVE",
            "B-LOC",
            "I-LOC",
            "B-ORG",
            "I-ORG"
            ]
    elif mode == "arg":
        return [
            #"Facility-Arg",
            #"Cause-Arg",
            "DeathVictim-Arg",
            "Vehicle-Arg",
            "Height-Arg",
            #"FromTo-Arg",
            #"Delta-Arg",
            #"Length-Arg",
            #"Central-Arg",
            #"Repeat-Arg",
            #"Reporter-Arg",

           # "Depth-Arg",

           # "AffectedCities-Arg",
            #"AffectedDistrict-Arg",
           # "AffectedFacility-Arg",
            #"AffectedFamily",
            #"AffectedFamily-Arg",
            #"AffectedField-Arg",

            #"AffectedHouse-Arg",
            #"AffectedInfrastructure-Arg",
            #"AffectedPeople",
            #"AffectedPeople-Arg",
            #"AffectedRT-Arg",
            #"AffectedVehicle-Arg",
            #"AffectedVehicles-Arg",
            #"AffectedVillage",
            #"AffectedVillage-Arg",

            "OfficerOfficial-Arg",

            #"DispatchedTrucks-Arg",
            "Place-Arg",
            #"Plate-Arg",

            "Time-Arg",

            #"Point-Arg",

            #"MonetaryLoss-Arg",
            #"Hospital-Arg",
            #"WoundVictim-Arg",

            #"Spot-Arg",
            #"Origin-Arg",

            "Street-Arg",
            "Strength-Arg",
            #"Strength_Arg",
            #"Published-Arg",
            #"Duration-Arg",
            #"Evacuee-Arg"
            ]
    elif mode == "secondaryevent":
        return ["RAIN-EVENT",
            "JAM-EVENT",
            "LANDSLIDE-EVENT",
            "MEETING-EVENT",
            "EVACUATE-EVENT"]
    elif mode == "event":
        return ["QUAKE-EVENT",
            "ACCIDENT-EVENT",
            "FLOOD-EVENT",
            "FIRE-EVENT" ]
    elif mode == "ploc":
        return [
            "LOC",
            "PLOC",
            ]
        

#%%
#p = re.compile('((satu|dua|tiga|empat|lima|enam|tujuh|delapan|sembilan|sepuluh) ?(buah|belas|puluh|ratus|ribu|juta)?|\d+\,?\d*) *((sr|km|kk|richter|orang|tewas|luka|hilang|terendam|tenggelam|mobil|rumah|motor|kendaraan|sedan)\s?)+')


p2 = re.compile("((kerugian|pusat gempa|kedalaman gempa|kedalaman|ketinggian|setinggi|sedalam|sepanjang|beradius|berkedalaman|selebar|sebesar|magnitudenya|magnitude|magnitudo \(m\)|magnitudo \( m \)|magnitudo|berkekuatan|skala|menewaskan|meninggal|membantai|tewaskan|macet|melibatkan)\s)?"
"((mencapai|diperkirakan|air)+ )*((((se)?)lutut|((se)?)paha|((se)?)dengkul|((se)?)leher|((se)?)pinggang|((se)?)perut|((se)?)dada|sejumlah|seluruh|semua|seperempat|sepertiga|setengah|separuh|satu|tidak ada|(ke)?dua|(ke)?tiga|(ke)?empat|(ke)?lima|(ke)?enam|(ke)?tujuh|(ke)?delapan|(ke)?sembilan|(ke)?sepuluh|puluhan|ratusan|ribuan|lusinan|jutaan|milyaran|trilyunan|tak ada) ?"+
"(se)?(buah|belas|puluh|ratus|ribu|juta|milyar|trilyun)?|iii|iv|v|vi|viii|ix|\d+(\,|\.)?\d* ?(- ?\d+(\,|\.)?\d* )?|(ratus|ribu|juta|milyar|trilyun)?) *"+
"(((se)?kali|unit|rupiah|dolar|(se)?juta|(se)?milyar|(se)?trilyun|sr|skala richter|sig|mmi|cm|centimeter|sentimeter|(se)?meter|km|kilometer|hektar|ha|kk|richter|titik api|titik longsor|titik|(se)?jam|(se)?menit|(se)?detik|(se)?bulan|(se)?hari|(se)?minggu|(se)?pekan|dekade"+
"itu|telah|orang|kakak beradik|menjadi|mengalami|ditemukan|tercatat|masih|korban jiwa|jiwa|korban|warga( \w+)?|petugas|warga|tewas|gugur|mati|wafat|jenazah|terbunuh|dibunuh|pengungsi|diungsikan|dievakuasi|mengungsi|meninggal|jenaazah|luka|terluka|hilang|terdampak|terkena dampak|"+
"terimbas|terisolir|terendam|tenggelam|rusak|terbakar|jebol|ambles|rubuh|roboh|ambrol|ambruk|"+
"runtuh|retak|hancur|mobil|armada|rumah|lahan|tempat tinggal|gedung|bangunan|desa|kecamatan|kelurahan|motor|kendaraan|sedan|yang)\s?)*", re.IGNORECASE)

def testarg_suite(s):
    test_sents = ['100 meter','semeter','dua ratus meter','semenit', 'berkekuatan 5.1 SR', 'berkekuatan 5.1 skala richter']
    for t in test_sents:
        print(is_numeric_arg(t))

def test_arg(s):
    return extract_arg([[w] for w in s.split()],0)

def is_vague(w):
    return inlist(w, vague)

def is_numeric_arg(w):
    return p2.match(w)

p3 = re.compile('km\s\d+(\+\d\d\d)?', re.IGNORECASE)
def is_km(w):
    return p3.match(w)

p4 = re.compile('((J|j)alur|(J|j)alan|(J|j)l)\.?\s(Raya\s)?([A-Z][a-z]*(\s)?)+')
def is_road(w):
    return p4.match(w)

p7 = re.compile('\d+(\.\d{1,2})? ?(LS|Lintang Selatan|LU|Lintang Utara|Bujur Barat|BB|Bujur Timur|BT)', re.IGNORECASE)
def is_coordinate(w):
    return p7.match(w)


p9 = re.compile('(sebelah)?(utara|selatan|barat|timur|tenggara|barat daya|barat laut|timur laut)\s?\w*')
def is_direction(w):
    return p9.match(w, re.IGNORECASE)

geographical_list =  [k[0] for k in geographical_landmarks]
p10 = re.compile('('+'|'.join(geographical_list)+')(\s[A-Z]\w+)', re.IGNORECASE)
def is_geographical(w):
    return p10.match(w)

p11 = re.compile('senin|selasa|rabu|kamis|jumat|sabtu|minggu', re.IGNORECASE)
def is_day(w):
    return p11.match(w)



def extract_org(sent, i):
    #return "F" # <<
    ''' extract organization '''
    global debug_mode

    if i <= len(sent) - 4:
        r = is_org(sent[i][0]+ " " + sent[i+1][0] + " " + sent[i+2][0] + " " + sent[i+3][0])
        if r > 0:
            return str(r)
        else:
            return 'F'
    if i <= len(sent) - 3:
        r = is_org(sent[i][0]+ " " + sent[i+1][0] + " " + sent[i+2][0] )
        if r > 0:
            return str(r)
        else:
            return 'F'
    elif i <= len(sent) - 2:
        r = is_org(sent[i][0]+ " " + sent[i+1][0] )
        if r > 0:
            return str(r)
        else:
            return 'F'
    elif i <= len(sent) - 1:
        r = is_org(sent[i][0] )
        if r > 0:
            return str(r)
        else:
            return 'F'
    else:
        return 'F'

disable_geofeatures = True

def extract_geo(sent, i):

    if i <= len(sent) - 2:
        r = is_geoevent(sent[i][0]+ " " + sent[i+1][0])
        if r:
            return str(len(r.group(0).split(' ')))
        else:
            return 'F'
    else:
        return 'F'

def lookahead(sent, i, num):
    ''' getting sent[i] + sent[i+1] + sent[i+2] +  ... + sent[i+num] separated by space '''
    name = sent[i][0]

    for idx in range(1, min(i+num, len(sent))):
        name = name + " " + sent[idx][0]
    return name


def extract_arg(sent, i):
    ''' in the window of 6 words, extract argument according to the following extractor '''

    for n in [6,5,4,3,2,1]:
        s = lookahead(sent, i, n)
        r = is_numeric_arg( s ) or is_coordinate( s ) or is_nopol( s ) or is_numeric_arg( s )\
        or is_road( s ) or is_km( s ) or is_geographical( s ) or is_rtwr( s ) or is_date( s )\
        or is_day( s ) or is_vehicle( s ) or in_tol(t)
        if r:
            split = r.group(0).split(' ')
            filtered = [w for w in r.group(0).split(' ') if w != ""]
            return str(len(filtered))
    return 'F'

org_seq = 0
arg_seq = 0
geo_seq = 0
total_sents = 0
sent_idx = 0
_prevadm = 'X'
_prev_ismax = 'O'

ploc_options = 'ismax|event|arg' # best so far is this combo

#%%
def word2features_ploc(sent, i):
    ''' constructing word features for pseudoloc detection '''
    global total_sents
    global _prevadm
    global _prev_ismax
    global geo_seq
    global org_seq
    
    word = sent[i][0]
    event = sent[i][4]
    entity = sent[i][2]
    postag = sent[i][1]
    
    if org_seq <= 0:
        org_code = extract_org(sent, i)
        if org_code == "F":
            org_seq = 0
        else:
            org_seq = int(org_code)

    org = "T" if (org_seq>0) else "F"
    org_seq = org_seq - 1
    
    if 'Arg' in event:
        event = 'O'
    entity = sent[i][2] 
    
    arg = sent[i][4]
    if 'EVE' in arg:
        arg = 'O'
    
    if geo_seq <= 0:
        geo_code = extract_geo(sent, i)
        if geo_code == "F":
            geo_seq = 0
        else:
            geo_seq = int(geo_code)

    geo = "T" if (geo_seq>0) else "F"
    geo_seq = geo_seq - 1
        
    adm_level = 'X'
    ismax = 'O'
    if 'B-PLOC' in entity or 'B-LOC' in entity:

        adm_level = str(sent[i][6])
        ismax = str(sent[i][7]) # prefilled by load_annotation function
        
        if verbosity >= 3:
            print ("t, adm_level, ismax=", sent[i] , adm_level, ismax)
        _prevadm = adm_level
        _prev_ismax = ismax
        adm_level = 'B' + adm_level
        
    elif 'I-PLOC' in entity or 'I-LOC' in entity:
        adm_level = 'I' + _prevadm
        ismax = _prev_ismax
        
    word_lower = word.lower()
    if i>0:
        word0 = sent[i-1][0]
    else:
        word0 = ''
    
    features = {
        'bias': 1.0,
        'word.lower()': word_lower,
       }   
    if 'entity' in ploc_options:
        features['word.entity'] = entity
    if 'event' in ploc_options:
        features['word.event'] = event
    if 'adm_level' in ploc_options:
        features['word.adm_level'] = adm_level
    if 'ismax' in ploc_options:
        features['word.ismax'] = ismax
    if 'postag' in ploc_options:
        features['postag'] = postag
        features['postag[:2]'] = postag[:2]
    if 'gaz' in ploc_options:
        features['word.geo'] = is_toponym(word)    
    if 'ev_keywords' in ploc_options:
        features['word.is_geospatial_ev_keywords'] = geo
    if 'org_regex' in ploc_options:
        features['word.org'] = org # is_org(word), #marker for ORG, ex. RSUD [Bangkalan] = PLOC of Bangkalan
    if 'arg_regex' in ploc_options:
        features['word.arg'] = arg # ???  what if we remove this ??? for event detection, the arg looks not very useful.

    return features
    
#%%
event_options = 'ev_keywords|entity'

def word2features_event(sent, i):
    ''' constructing word features for event detection '''
    global event_options
    global total_sents
    global arg_seq
    global geo_seq
    global org_seq
    word = sent[i][0]
    postag = sent[i][1]
    entity = sent[i][2] # <-- this field will not be used (i.e will be overwritten) on the prediction, but will be used on the train mode.
    
    word_lower = word.lower()

    if org_seq <= 0:
        org_code = extract_org(sent, i)
        if org_code == "F":
            org_seq = 0
        else:
            org_seq = int(org_code)

    org = "T" if (org_seq>0) else "F"
    org_seq = org_seq - 1

    if arg_seq <= 0:
        arg_code = extract_arg(sent, i)
        #print(arg_code)
        if (arg_code == "T") or (arg_code == "1"):
            arg_seq = 1
            #print("extracting 1:", sent[i])
        elif (arg_code == "F"):
            arg_seq = 0
            #print("skipping 1:", sent[i])
        else:
            arg_seq = int(arg_code)
            #print("extracting arg", arg_seq, sent[i])

    arg = "T" if (arg_seq>0) else "F"
    arg_seq = arg_seq - 1

    if geo_seq <= 0:
        geo_code = extract_geo(sent, i)
        if geo_code == "F":
            geo_seq = 0
        else:
            geo_seq = int(geo_code)

    geo = "T" if (geo_seq>0) else "F"
    geo_seq = geo_seq - 1

    features = {
        'bias': 1.0,
        'word.lower()': word_lower,
        'word.isupper()': word.isupper(),
        'word.istitle()': word.istitle(),
        'word.isdigit()': word.isdigit(),
 
    }
    if 'entity' in event_options:
        features['word.entity'] = entity
    if 'postag' in event_options:
        features['postag'] = postag
        features['postag[:2]'] = postag[:2]
    if 'gaz' in event_options:
        features['word.geo'] = is_toponym(word)
    if 'org_regex' in event_options:
        features['word.org'] = org # is_org(word), #marker for ORG, ex. RSUD [Bangkalan] = PLOC of Bangkalan
    if 'ev_keywords' in event_options:
        features['word.is_geospatial_ev_keywords'] = geo
    if 'arg_regex' in event_options:
        features['word.arg'] = arg # ???  what if we remove this ??? for event detection, the arg looks not very useful.
    #look backward
    if i > 0:
        word0 = sent[i-1][0]
        word0_lower = word0.lower()
        postag0 = sent[i-1][1]
        entity0 = sent[i-1][2]
        features.update({
            '-1:word.lower()': word0_lower,
            '-1:word.istitle()': word0.istitle(),
            '-1:word.isupper()': word0.isupper(),
        })
        if 'entity' in event_options :
            features.update({
                    '-1:word.entity': entity0
            })
        
        if 'postag' in event_options :
            features['-1:postag'] = postag0
            features['-1:postag[:2]']= postag0[:2]
           
        if 'gaz' in event_options:
            features['-1:word.geo'] = is_toponym(word0 + ' ' + word)
    else:
        features['BOS'] = True

    #look forward
    if i < len(sent)-1:
        word1 = sent[i+1][0]
        word1_lower = word1.lower()
        postag1 = sent[i+1][1]
        entity1 = sent[i+1][2]
        features.update({
            '+1:word.lower()': word1_lower,
            '+1:word.istitle()': word1.istitle(),
            '+1:word.isupper()': word1.isupper(),

        })
        if 'entity' in event_options :
            features.update({
                    '+1:word.entity': entity1
            })
        if 'postag' in event_options:
            features['+1:postag'] = postag1
            features['+1:postag[:2]'] = postag1[:2]
    else:
        features['EOS'] = True

    return features

#%%
arg_options = 'arg_regex|event|entity|gaz|ev_keywords'

def word2features_arg(sent, i):
    ''' constructing word features for arg detection '''
    ''' todo: fix the 'event' if that appear in arg_options '''
    global total_sents
    global arg_seq
    global geo_seq
    global org_seq
    word = sent[i][0]
    postag = sent[i][1]
    entity = sent[i][2]
    event = sent[i][4] # <-- this field will not be used (overwritten) on the prediction, but will be used on the train mode.
    
    if 'Arg' in event:
        event = 'O'
    
    labels = configLabels("arg")
    if sent[i][3] in labels: 
        event = sent[i][3]
    else:
        event = "O"
    
    word_lower = word.lower()

    if org_seq <= 0:
        org_code = extract_org(sent, i)
        if org_code == "F":
            org_seq = 0
        else:
            org_seq = int(org_code)

    org = "T" if (org_seq>0) else "F"
    org_seq = org_seq - 1

    if arg_seq <= 0:
        arg_code = extract_arg(sent, i)
        #print(arg_code)
        if (arg_code == "T") or (arg_code == "1"):
            arg_seq = 1
            #print("extracting 1:", sent[i])
        elif (arg_code == "F"):
            arg_seq = 0
            #print("skipping 1:", sent[i])
        else:
            arg_seq = int(arg_code)
            #print("extracting arg", arg_seq, sent[i])

    arg = "T" if (arg_seq>0) else "F"
    arg_seq = arg_seq - 1

    if geo_seq <= 0:
        geo_code = extract_geo(sent, i)
        if geo_code == "F":
            geo_seq = 0
        else:
            geo_seq = int(geo_code)

    geo = "T" if (geo_seq>0) else "F"
    geo_seq = geo_seq - 1

    features = {
        'bias': 1.0,
        'word.lower()': word_lower,
        'word.isupper()': word.isupper(),
        'word.istitle()': word.istitle(),
        'word.isdigit()': word.isdigit(),

    }
    
    if 'postag' in arg_options:
        features['postag'] = postag
        features['postag[:2]'] = postag[:2]
    if 'ev_keywords' in arg_options:
        features['word.is_geospatial_ev_keywords'] = geo
    if 'arg_regex' in arg_options:
        features['word.arg'] = arg

    if 'org_regex' in arg_options:
        features['word.org'] = org 
    if 'gaz' in arg_options:
        features['word.geo'] = is_toponym(word)
    if 'entity' in arg_options:
        features['word.entity'] = entity
    if 'event' in arg_options:
        features['word.event'] = event    

    #look backward
    if i > 0:
        word0 = sent[i-1][0]
        word0_lower = word0.lower()
        postag0 = sent[i-1][1]
        entity0 = sent[i-1][2]
        event0 = sent[i-1][4]
        if 'Arg' in event0:
            event0 = 'O'
        features.update({
            '-1:word.lower()': word0_lower,
            '-1:word.istitle()': word0.istitle(),
            '-1:word.isupper()': word0.isupper(),

        })
        if 'entity' in arg_options :
            features.update({
                    '-1:word.entity': entity0
            })
        if 'event' in arg_options:
            features['-1:word.event'] = event0    
        if 'postag' in arg_options:
            features['-1:postag'] = postag0
            features['-1:postag[:2]'] = postag0[:2]
        if 'gaz' in arg_options:
            features['-1:word.geo'] = is_toponym(word0 + ' ' + word)            
            
    else:
        features['BOS'] = True

    #look forward
    if i < len(sent)-1:
        word1 = sent[i+1][0]
        word1_lower = word1.lower()
        postag1 = sent[i+1][1]
        entity1 = sent[i+1][2]
        event1 = sent[i+1][4]
        if 'Arg' in event1:
            event1 = 'O'        
            
        features.update({
            '+1:word.lower()': word1_lower,
            '+1:word.istitle()': word1.istitle(),
            '+1:word.isupper()': word1.isupper(),
        })
        
        if 'entity' in arg_options :
            features.update({
                    '+1:word.entity': entity1
            })
        if 'event' in arg_options:
            features['+1:word.event'] = event1    
        if 'postag' in arg_options:
            features['+1:postag'] = postag1
            features['+1:postag[:2]'] = postag1[:2]

    else:
        features['EOS'] = True

    return features

#%%
entity_options = 'org_regex|arg_regex|ev_keywords|gaz|postag' 
def word2features_entity(sent, i):
    global total_sents
    global arg_seq
    global geo_seq
    global org_seq
    word = sent[i][0]
    postag = sent[i][1] #!!!
    word_lower = word.lower()

    if org_seq <= 0:
        org_code = extract_org(sent, i)
        if org_code == "F":
            org_seq = 0
        else:
            org_seq = int(org_code)

    org = "T" if (org_seq>0) else "F"
    org_seq = org_seq - 1

    if arg_seq <= 0:
        arg_code = extract_arg(sent, i)
        #print(arg_code)
        if (arg_code == "T") or (arg_code == "1"):
            arg_seq = 1
            #print("extracting 1:", sent[i])
        elif (arg_code == "F"):
            arg_seq = 0
            #print("skipping 1:", sent[i])
        else:
            arg_seq = int(arg_code)
            #print("extracting arg", arg_seq, sent[i])

    arg = "T" if (arg_seq>0) else "F"
    arg_seq = arg_seq - 1

    if geo_seq <= 0:
        geo_code = extract_geo(sent, i)
        if geo_code == "F":
            geo_seq = 0
        else:
            geo_seq = int(geo_code)

    geo = "T" if (geo_seq>0) else "F"
    geo_seq = geo_seq - 1

    features = {
        'bias': 1.0,
        'word.lower()': word_lower,
        'word.isupper()': word.isupper(),
        'word.istitle()': word.istitle(),
        'word.isdigit()': word.isdigit(),
    }
    
    if 'postag' in entity_options:
        features['postag'] = postag
        features['postag[:2]'] = postag[:2]
    if 'gaz' in entity_options:
        features['word.geo'] = is_toponym(word)
    if 'org_regex' in entity_options:
        features['word.org'] = org # is_org(word), #marker for ORG, ex. RSUD [Bangkalan] = PLOC of Bangkalan
    if 'ev_keywords' in entity_options:
        features['word.is_geospatial_ev_keywords'] = geo
    if 'arg_regex' in entity_options:
        features['word.arg'] = arg
    
    #look backward
    if i > 0:
        word0 = sent[i-1][0]
        word0_lower = word0.lower()
        postag0 = sent[i-1][1]
        features.update({
            '-1:word.lower()': word0_lower,
            '-1:word.istitle()': word0.istitle(),
            '-1:word.isupper()': word0.isupper(),
        })
        if 'postag' in entity_options:
            features['-1:postag'] = postag0
            features['-1:postag[:2]'] = postag0[:2]
        if 'gaz' in entity_options:
            features['-1:word.geo'] = is_toponym(word0 + ' ' + word)
    else:
        features['BOS'] = True

    #look forward
    if i < len(sent)-1:
        word1 = sent[i+1][0]
        word1_lower = word1.lower()
        postag1 = sent[i+1][1]
        features.update({
            '+1:word.lower()': word1_lower,
            '+1:word.istitle()': word1.istitle(),
            '+1:word.isupper()': word1.isupper(),
        })
        if 'postag' in entity_options:
            features['+1:postag'] = postag1
            features['+1:postag[:2]'] = postag1[:2]       
    else:
        features['EOS'] = True

    return features

#%%
def sent2features(sent, mode="entity"):
    global sent_idx
    global total_sents
    sent_idx = sent_idx + 1
    if sent_idx % 100 == 0: print("processing ", sent_idx, "/", total_sents, "pct", sent_idx * 100.0 / total_sents, "%")
    if mode == "entity":
        return [ word2features_entity(sent, i) for i in range(len(sent)) ]
    elif mode == "event":
        return [ word2features_event(sent, i) for i in range(len(sent)) ]
    elif mode == "arg":
        return [ word2features_arg(sent, i) for i in range(len(sent)) ]
    elif mode == "ploc":
        return [ word2features_ploc(sent, i) for i in range(len(sent)) ]
    
#%%
def sent2labels(sent, mode = "entity"):
    labels = []
    label_index = 0
    if mode == "entity":
        label_index = 2
    elif mode == "event" or mode == "arg" :
        label_index = 4
    elif mode == "ploc" :
        label_index = 5
    for w in sent:
        if label_index > len(w) - 1:
            # print ("out of range", w)
            # print ("label_index", label_index)
            labels.append('O')
        else:
            if mode=="arg" and '-Arg' in w[label_index]:
                labels.append(w[label_index])
            elif mode =="event" and '-EVE' in  w[label_index]:
                labels.append(w[label_index])
            elif mode == "entity" or mode== "ploc":
                labels.append(w[label_index])
            else:
                labels.append('O')
        
    return labels

def sent2tokens(sent):
    labels = []
    for w in sent:
        labels.append(w[0])
    return labels

def load_disambiguations(f):
    ''' load experiment on disambiguation file '''
    lines = []
    with open(f, encoding="utf8") as fh:
        doc = fh.readlines()

''' usage ex:
    debug("jaya")
    r = debug("jaya") <-- list of all matches are stored in r
    r[0] <-- first matching word
    next(r[-1]) <-- next adjacent word from last matching word
'''
def debug(w, label=None):

    matches = []
    for sent in X:
        for word in sent:
            if word["word.lower()"] == w:
                matches.append(word)
    return matches

''' previous cursor word '''
def prev(w):
    _prev = None
    for sent in X:
        for word in sent:
            if word == w:
                return _prev
            _prev = word

def next(w):
    _prev = None
    for sent in X:
        for word in sent:
            if _prev == w:
                return word
            _prev = word
            
#%%            
MAXES = []
def load_annotation(f, stripdocs = False, noploc = True, predictMode = False):
    ''' load experiment file for sequence labeling
        format of file: Word/POS_TAG/ENTITY_TYPE/ENTITY_ROLE

        Kerabat/NNP/O/O
        Layat/NNP/O/O
        Jasad/NNP/O/O
        Jerry/NNP/O/O
        Wong/NNP/O/O
        Pengemudi/NNP/O/O
        Mini/NNP/B-ARG/Vehicle-Arg
        Cooper/NNP/I-ARG/Vehicle-Arg
        di/IN/O/O
        RSCM/NN/B-ORG/Hospital-Arg
        -/-/O/O
        -/NNP/O/O
        Jakarta/NNP/B-LOC/Published-Arg/(-6.197602429787846, 106.83139222722116)/2
        -/-/O/O
        Jenazah/NNP/O/O
        Jerry/NNP/O/O
        Wong/NNP/O/O
        ,/,/O/O
        pengemudi/NN/O/O
        Mini/NNP/B-ARG/Vehicle-Arg
        Cooper/NNP/I-ARG/Vehicle-Arg
        yang/SC/O/O
        menabrak/VBT/B-EVE/ACCIDENT-EVENT
        bagian/O/O
        belakang/NN/O/O
        truk/NN/B-ARG/Vehicle-Arg
        ,/,/O/O
        kini/RB/O/O
        berada/VBI/O/O
        di/IN/O/O
        RSCM/NNP/B-ORG/Hospital-Arg
        
        Note: This function is also called by the predict() function, 
        but with parameter predictMode = True.
        
        
    '''
    global MAXES
    global doc
    MAXES = [] # reset maximum adm level for each articles
    
    sentences = []
    sent = []
    
    print ("open annotation",os.path.abspath(f))
    with open(f, encoding="utf8") as fh:
        doc = fh.readlines()
        
    # first loop is to find out max adm level for each article
    i = 0
    articleidx = 0
    max_admlev = 0
    admlev = 0
    
    for line in doc:
        tokens = line.split("/")
        if len(tokens) == 6 and "DD" not in tokens:
            if verbosity == 2 :
                print (tokens)
            try:
                admlev = int(tokens[5])
            except:
                admlev = 0
            if admlev > max_admlev :
                max_admlev = admlev
                
        if line.startswith( "===" ):
            if verbosity == 2:
                print("new doc ===")
            articleidx = articleidx + 1
            MAXES.append( max_admlev )
            max_admlev = 0 
        i = i + 1               
    # second loop
    i = 0
    articleidx = 0
    for line in doc:

        if line.startswith( "===" ):
            if verbosity == 2 :
                print("detecting new line")
            articleidx = articleidx + 1
            if not stripdocs: sentences.append(["==="])
            continue

        tokens = line.split("/")
        if "DD" in tokens:

            # print (tokens, " at line ", i)
            if len(tokens) > 5:
                date = "/".join(tokens[:3])
                postag = tokens[3]
                label = tokens[4]
                role_label = tokens[5]
            else:
                date = "/".join(tokens[:2])
                postag = tokens[2]
                label = tokens[3]
                role_label = tokens[3]
            sent.append([date, postag, label.rstrip(), None, role_label.strip()])


        elif len(tokens) == 4 or len(tokens) == 6 : # num of tokens is six if B-LOC or B-PLOC . the last token is admin level, before that is (lat, lng) format.
            label = tokens[2].rstrip()
            #  Kampung/NNP/B-LOC/Place-Arg/(-3.220507894108893, 107.64114141584496)/2
            #    0      1    2      3           4                                   5
            if len(tokens) == 6 and predictMode == False:
                loc = tokens[4].strip()
                admin = tokens[5]
                if verbosity == 2 :
                    print("tokens",tokens)
                    print(articleidx)
                    print("predictMode", predictMode)
                ismaxlev = MAXES[articleidx] == int(admin)
                if verbosity == 2 :
                    print(tokens[0], ismaxlev)
            else:
                loc = None
                admin = None
                ismaxlev = None
            role_label = tokens[3].strip()
            if label.find("PLOC") >= 0:
                ploc = "PLOC"
            elif label.find("LOC") >= 0:
                ploc = "LOC"
            else:
                ploc = "O"
                
            if noploc:
                #print(tokens[0], tokens[1], label.replace("PLOC","LOC"))
                sent.append([tokens[0], tokens[1], label.replace("PLOC","LOC"), loc, role_label, ploc, admin, ismaxlev]) # most usage
                #                  0     1              2                        3        4        5    6         7
            else:
                sent.append([tokens[0], tokens[1], label, loc, role_label, ploc, admin, ismaxlev])

        elif len(tokens)<=1: #new sent

            sentences.append(sent)
            sent = []
        i = i + 1
    return sentences
'''
 for sent in X:
    for word in sent:
        for item in word.items():
            if item[0] is None or item[1] is None: print (item)

for sent in y_train:
    for word in sent:
        for item in word:
            if item=="": print(word)
'''

#%%
_mode = ""
sequence = ["", "entity", "event", "arg", "ploc"]
y_test_list = {} # for merging from earlier phase
y_train_list = {} # for merging from earlier phase

crf_entity = {}
crf_event = {}
crf_arg = {}
crf_ploc = {}

#%%
def train_crf( cross_validation=False, skipFeatureBuilding=False, mini=False, rnd = 1, mode = "entity", max_iterations = 100, _c1 = 0.1, _c2 = 0.1, test_size = 0.2):
    ''' train the crf with these arguments:
        cross validation option : whether we use the CV (deafult to 3 folds)
        skipFeatureBuilding : whether we skip the feature building
        mini: whether we use the mini set (training-mini.txt) or not.
        mode: whether "entity" or "event".
            "entity" : classify as four entity tags: ORG, LOC, ARG, EVE
            "event" : classify each as Event. needs train_crf from earlier mode ("entity")
            "arg" : argument classification
    '''

    ''' here's global variables that is affected by calling this function '''
    global crf_entity, crf_event, crf_arg, crf_ploc
    global y_pred
    global y_test_list
    global y_train_list
    global X_test
    global y_test
    global X
    global y
    global sent_idx
    global total_sents
    global X_train
    global y_train
    global _mode
    global sents

    

    _mode = mode
    
    ''' this is what consumes most time, constructing features. we will skip this step
        if skipFeatureBuilding is mentioned or mode is "entity"
    '''
    if not skipFeatureBuilding or mode == "entity":
        if mini:
            sents = load_annotation("G:/Riset/Gatotkaca/Exp06-Extraction/"+ dataset_folder +"/training-mini.txt", True)
        else:
            sents = load_annotation("G:/Riset/Gatotkaca/Exp06-Extraction/"+ dataset_folder +"/training.txt", True)

        total_sents = len(sents)
        sent_idx = 0
        print("training", total_sents, "sentences")

        X = [sent2features(s, mode) for s in sents]
        y = [sent2labels(s, mode) for s in sents]
        

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size= test_size, random_state = rnd)
        if mode == "event" :            
            if 'entity' in event_options:
                print("merge the X_train's word.entity feature using y_train from previous train session")
                for ix, sent in enumerate(y_train_list["entity"]):
                    #print("sent #", ix)
                    for iy, entity in enumerate(sent):
                        #print("ent #", iy)
                        X_train[ix][iy]["word.entity"] = entity
                        if iy > 0:
                            X_train[ix][iy]["-1:word.entity"] = sent[iy-1]
                        if iy < len(sent) - 1:
                            X_train[ix][iy]["+1:word.entity"] = sent[iy+1]
        if mode == "arg" :            
            if 'entity' in arg_options:
                print("merge the X_train's word.entity feature using y_train from previous train session")
                for ix, sent in enumerate(y_train_list["entity"]):
                    #print("sent #", ix)
                    for iy, entity in enumerate(sent):
                        #print("ent #", iy)
                        X_train[ix][iy]["word.entity"] = entity
                        if iy > 0:
                            X_train[ix][iy]["-1:word.entity"] = sent[iy-1]
                        if iy < len(sent) - 1:
                            X_train[ix][iy]["+1:word.entity"] = sent[iy+1]
            if 'event' in arg_options:
                print("merge the X_train's word.event feature using y_train from previous train session")
                for ix, sent in enumerate(y_train_list["event"]):
                    #print("sent #", ix)
                    for iy, entity in enumerate(sent):
                        #print("ent #", iy)
                        X_train[ix][iy]["word.event"] = entity
                        if iy > 0:
                            X_train[ix][iy]["-1:word.event"] = sent[iy-1]
                        if iy < len(sent) - 1:
                            X_train[ix][iy]["+1:word.event"] = sent[iy+1]
        if mode == "ploc" :            
            if 'entity' in ploc_options:
                print("merge the X_train's word.entity feature using y_train from previous train session")
                for ix, sent in enumerate(y_train_list["entity"]):
                    #print("sent #", ix)
                    for iy, entity in enumerate(sent):
                        #print("ent #", iy)
                        X_train[ix][iy]["word.entity"] = entity
                        if iy > 0:
                            X_train[ix][iy]["-1:word.entity"] = sent[iy-1]
                        if iy < len(sent) - 1:
                            X_train[ix][iy]["+1:word.entity"] = sent[iy+1]
            if 'event' in ploc_options:
                print("merge the X_train's word.event feature using y_train from previous train session")
                for ix, sent in enumerate(y_train_list["event"]):
                    #print("sent #", ix)
                    for iy, entity in enumerate(sent):
                        #print("ent #", iy)
                        X_train[ix][iy]["word.event"] = entity
                        if iy > 0:
                            X_train[ix][iy]["-1:word.event"] = sent[iy-1]
                        if iy < len(sent) - 1:
                            X_train[ix][iy]["+1:word.event"] = sent[iy+1]
            if 'arg' in ploc_options:
                print("merge the X_train's word.arg feature using y_train from previous train session")
                for ix, sent in enumerate(y_train_list["arg"]):
                    #print("sent #", ix)
                    for iy, entity in enumerate(sent):
                        #print("ent #", iy)
                        X_train[ix][iy]["word.arg"] = entity
                        if iy > 0:
                            X_train[ix][iy]["-1:word.arg"] = sent[iy-1]
                        if iy < len(sent) - 1:
                            X_train[ix][iy]["+1:word.arg"] = sent[iy+1]
        y_train_list[mode] = y_train
    '''
    full cycle
    1.  train_crf with test train split with "entity" mode .
    2.  y_pred is kept, then fetch to the next train_crf with "event" mode.
        the X_train, X_test, y_train, y_test need to be retained .
    3.  the y_pred is now going to be used to overwrite the X_test on the "event" mode. 
        basically this is saying that the entity detected by our model on the entity detection will be used for 
        event detection and will be checked for the performance as well (on test only)
        if the entity detected was to be supplied with the annotation's entity field, we can not test the efficiency of 
        the classifier of the entity detection. this is of course not true with the X train. 
        We can still use annotated X_train to train.
        
    '''

    crf = sklearn_crfsuite.CRF(
        algorithm = 'lbfgs',
        c1 = _c1,
        c2 = _c2,
        max_iterations = max_iterations,
        all_possible_transitions=True
    )
    


    if cross_validation:
        params_space = {
        'c1': scipy.stats.expon(scale=0.5),
        'c2': scipy.stats.expon(scale=0.05),
        }
        labels = configLabels(mode)

        # use the same metric for evaluation
        f1_scorer = make_scorer(metrics.flat_f1_score,
                                average='weighted', labels=labels)

        # search
        rs = RandomizedSearchCV(crf, params_space,
                                cv=10,
                                verbose=1,
                                n_jobs=-1,
                                n_iter=20,
                                scoring=f1_scorer)

        rs.fit(X_train, y_train)

        # crf = rs.best_estimator_
        print('best params:', rs.best_params_)
        print('best CV score:', rs.best_score_)
        #print('model size: {:0.2f}M'.format(rs.best_estimator_.size_ / 1000000))
        crf = rs.best_estimator_
    else:
        crf.fit(X_train, y_train)

    # labels = list(crf.classes_) <-- this is only if we wanted to check the actual labels from the training data

    labels = configLabels(mode)
    print (labels)
    # group B and I results
    sorted_labels = sorted(
        labels,
        key=lambda name: (name[1:], name[0])
    )
    
    print ("train mode=", mode)
    if mode == "entity":
        crf_entity = crf
        print("entity options:", entity_options)

    if mode == "event" :
        crf_event = crf
        # the y_pred is now going to be used to merge the X_test on the "*.entity" fields
        print("event options:", event_options)
        
        if 'entity' in event_options:
            
            print("merge the X_test's word.entity feature using y_test from previous train session")
            for ix, sent in enumerate(y_test_list["entity"]):
                for iy, entity in enumerate(sent):
                    X_test[ix][iy]["word.entity"] = entity
                    if iy > 0:
                        X_test[ix][iy]["-1:word.entity"] = sent[iy-1]
                    if iy < len(sent) - 1:
                        X_test[ix][iy]["+1:word.entity"] = sent[iy+1]
            
    if mode == "arg":
        crf_arg = crf
        print("arg options:", arg_options)
        if 'event' in arg_options: 
            
            print("merge the X_test's word.event feature using y_test from previous train session")
            for ix, sent in enumerate(y_test_list["event"]):
                for iy, event in enumerate(sent):
                    X_test[ix][iy]["word.event"] = event
                    if iy > 0:
                        X_test[ix][iy]["-1:word.event"] = sent[iy-1]
                    if iy < len(sent) - 1:
                        X_test[ix][iy]["+1:word.event"] = sent[iy+1]
        
        
        if 'entity' in arg_options:
            
            print("merge the X_test's word.entity feature using y_test from previous train session")
            
            for ix, sent in enumerate(y_test_list["entity"]):
                for iy, entity in enumerate(sent):
                    X_test[ix][iy]["word.entity"] = entity
                    if iy > 0:
                        X_test[ix][iy]["-1:word.entity"] = sent[iy-1]
                    if iy < len(sent) - 1:
                        X_test[ix][iy]["+1:word.entity"] = sent[iy+1]
                    
    if mode == "ploc":
        crf_ploc = crf
        print("ploc options:", ploc_options)
        if 'event' in ploc_options:
            
            print("merge the X_test's word.event feature using y_pred from previous train arg and event session")
            for ix, sent in enumerate(y_test_list["event"]):
                for iy, event in enumerate(sent):
                    X_test[ix][iy]["word.event"] = event
                    if iy > 0:
                        X_test[ix][iy]["-1:word.event"] = sent[iy-1]
                    if iy < len(sent) - 1:
                        X_test[ix][iy]["+1:word.event"] = sent[iy+1]
                        
        if 'arg' in ploc_options:           
            
            print("merge the X_test's word.arg feature using y_pred from previous train arg and event session")
            for ix, sent in enumerate(y_test_list["arg"]):
                for iy, arg in enumerate(sent):
                    X_test[ix][iy]["word.arg"] = arg
                    if iy > 0:
                        X_test[ix][iy]["-1:word.arg"] = sent[iy-1]
                    if iy < len(sent) - 1:
                        X_test[ix][iy]["+1:word.arg"] = sent[iy+1]
                        
        if 'entity' in ploc_options:
            
            print("merge the X_test's word.entity feature using y_pred from previous train session")
            for ix, sent in enumerate(y_test_list["entity"]):
                for iy, entity in enumerate(sent):
                    X_test[ix][iy]["word.entity"] = entity
                    if iy > 0:
                        X_test[ix][iy]["-1:word.entity"] = sent[iy-1]
                    if iy < len(sent) - 1:
                        X_test[ix][iy]["+1:word.entity"] = sent[iy+1]
                        
                    
    y_pred = crf.predict(X_test)        
    y_test_list[mode] = y_test #y_pred
    metrics.flat_f1_score(y_test, y_pred,
                          average='weighted', labels=labels)

    print(metrics.flat_classification_report(
        y_test, y_pred, labels=sorted_labels, digits=3
    ))

    return crf
#%%
def load_crf():
    global crf_entity, crf_event, crf_arg, crf_ploc
    pickle_in = open("crf.entity.pickle", "rb")
    crf_entity = pickle.load(pickle_in, encoding='latin1')

    pickle_in = open("crf.event.pickle", "rb")
    crf_event = pickle.load(pickle_in, encoding='latin1')
    
    pickle_in = open("crf.arg.pickle", "rb")
    crf_arg = pickle.load(pickle_in, encoding='latin1')
    
    pickle_in = open("crf.ploc.pickle", "rb")
    crf_ploc = pickle.load(pickle_in, encoding='latin1')
    print("crf entity and event loaded")
#%%
def save_crf():
    global crf_entity, crf_event, crf_arg, crf_ploc
    with open("crf.entity.pickle", 'wb') as f:
        pickle.dump(crf_entity, f)
    with open("crf.event.pickle", 'wb') as f:
        pickle.dump(crf_event, f)
    with open("crf.arg.pickle", 'wb') as f:
        pickle.dump(crf_arg, f)
    with open("crf.ploc.pickle", 'wb') as f:
        pickle.dump(crf_ploc, f)    
        
    print("crf entity and event saved")
#%%
def postag(input_str):
    # call ina-nlp library
    import os
    os.chdir('..\Exp14-INA-NLP')
    from subprocess import Popen, PIPE, STDOUT

    p = Popen(['java', '-cp', '.;ipostagger.jar;InaNLP.jar', 'InaPosTag'], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    grep_stdout = p.communicate(input=input_str.encode())[0]
    return grep_stdout.decode()
    os.chdir('..')

#%%
def breaklines(doc):
    lines = doc.split(". ")
    return lines

#%%
def breakwords(l):
    if verbosity == 2:
        print ("break ", l)
    words = l.split(" ")
    words2 = []
    for w in words:
        if w != "\n" and len(w)>0:
            words2.append( w + "/O/O" )
        else:
            words2.append( "\n" )
    return words2
#%%
def find_ambigus(t):
    ambigus = []
    if in_prov(t):
        ambigus.append( ['Prov', t] )
    if in_kk(t):
        k = d2.loc[t]
        p = k.NAME_1
        ambigus.append( ['Kab/Kota', t, p] )
    if in_kec(t):
        list_kab = d3[['KABUPATEN', 'PROPINSI']].loc[t]
        #for kab in list_kab:
        #    ambigus.append( ['Kec', t, 'Kab', kab, 'Prov', kab, 'Indonesia' ] )
        l = []
        for k in list_kab.iterrows():
            l.append((k[1][0], k[1][1]))
        filtered = set(l)
        for r in filtered:
            ambigus.append( ['Kec', t, r[0], r[1] ] )

    if in_desa(t):
       rows = d4[['KABUPATEN','KECAMATAN','PROPINSI']].loc[t]
       if isinstance(rows, pd.DataFrame):
           for r in rows.iterrows():
                ambigus.append( ['Desa/Kel', t, r[1].KECAMATAN, r[1].KABUPATEN, r[1].PROPINSI ] )
       elif isinstance(rows, pd.Series):
           ambigus.append( ['Desa/Kel', t, rows.KECAMATAN, rows.KABUPATEN, rows.PROPINSI ] )
    return ambigus
#%%
def get_admlevel(item):
    lvl = '5'
    
    if 'Village/Desa/Kel:' in item: 
        lvl = "4"
    elif 'Subdistrict/Kec:' in item:
        lvl = "3"
    elif 'City/Kota/Kab:' in item:
        lvl = "2"
    elif 'Province:' in item:
        lvl = "1"
    elif 'Country:' in item:
        lvl = "0"

    return lvl

#%%

def print_ambiguations(r, loc = None):
    ''' print the possible ambiguations from toponym r 
        loc is optional, containing the correct location lat long in string format
        if one of the ambiguation centroid matches loc , then it will be starred / -->
    '''
    for item in r:
        if loc:
            if loc in item: # correct one
                lvl = get_admlevel(item)
                if verbosity >= 2:
                    print ('-->' + item + '[' + lvl + ']' ) # inside < > is the admin level of the disambiguated place
            else:
                if verbosity >= 2:
                    print('-- ' + item)
        else:
            if verbosity >= 2:
                print('-- ' + item)
            
#%%
def print_ambiguations_pred(winner, t, loc):
    ''' print the predicted disambiguation from toponym t by lookup from winner list
        loc is the correct location lat long in string format.
        this function also maintains correct_pred and adding it by one for each correct prediction.
        this function evaluate whether winner indeed refer to t / loc pair (correct ref)
    '''
    global total_pred
    global correct_pred
    
    r = ambigus(t)
    for fullname in winner:
        if fullname in r:
            total_pred = total_pred + 1
            try:
                print (str(latlng(fullname)), loc)
                status = str(latlng(fullname)) in loc
            except:
                print ("exception at",fullname )
                status = False
            if status: correct_pred = correct_pred + 1
            print ('|predicted disambiguated value of',t,'=', fullname, 'status=', status  )

sents = []

''' 
hypothesis:
the ploc/loc classifier can be improved by using feature of geographical administration level for each toponym.

'''
#%%
def get_ambiguations():
    global sents
    sents = load_annotation("G:/Riset/Gatotkaca/Exp06-Extraction/"+ dataset_folder +"/training.txt")
    toponym_idx = 0
    for sent in sents:
        #print ("---")
        startCollect = False
        toponym = []
        for line in sent:
            if line == "===": print (line)
            #print(line)
            EOL = sent.index(line) == len(sent) - 1
            #if EOL: print ("EOL")
            if line[2] == 'B-LOC':
                 #start collecting tokens
                if line[0].lower() == "jl" or line[0].lower() == "jalan": continue

                loc = line[3]
                #print("LOC FOUND", loc)
                startCollect = True
                #print("startcollect")

            if startCollect:
                if line[2] == 'I-LOC' or line[2]=="B-LOC" and not EOL: #inside the LOC
                    toponym.append( line[0] )
                    #print("append2", line[0] )
                else: # finished collecting, change from B-I to O or to another B or EOL

                    if EOL :
                        #print("append3", line[0] )
                        toponym.append( line[0] )

                    toponym_found = ' '.join(toponym)
                    print ("*", toponym_found)

                    toponym_idx = toponym_idx + 1
                    print_ambiguations( ambigus(toponym_found), loc )
                    startCollect = False
                    loc = None
                    toponym = []
    print("total toponyms", toponym_idx)
#%%
def evaluate_winner(winner, toponyms, locs):
    '''
    winner is tuple of fullnames
    toponyms is list of placenames (LOC entities), ordered by the sequence it appeared in the doc
    for each of the t in toponyms we compare
    locs is the correct lat/long for each toponym obtained from the corpus
    ''' 
    if winner is None: 
        print("Winner is None")
        return
    
    i = 0
    print("found",len(toponyms)," toponyms:", toponyms)
    print("matched with ", len(locs), "ref locations:", locs)
    for t in toponyms:
        print_ambiguations_pred(winner, t, locs[i])
        i = i+1
        
#%%        
polygon_pts = []
def filter_duplicate_toponyms(toponyms):
    ''' return list of toponyms that is uniquely pointing to different lat long ambiguations
        if two or more toponyms present in the list that points to same lat long ambiguations, the first one gonna be used, 
        the rest gonna be discarded. 
        this is to speed up the disambiguate_document algorithm.
    '''
    regex = re.compile('(desa|kelurahan|kecamatan|provinsi|kabupaten|kota|dusun|propinsi|pulau) (.*)', re.IGNORECASE)
    res = []
    for t in toponyms:
        m = regex.match(t)  
        if m:
            strip = m.group(2).strip()
            res.append(strip)
        else:
            res.append(t)
    res2 = []
    for t in res:
        if in_gaz(t):
            res2.append(t)
        
    return list(set(res2))

#%%
import sys
from area import area
            
def disambiguate_document(toponyms, algorithm = "smcd-adm"):
    ''' toponyms are list of t in document, ex [
        'Jakarta', 'Jakarta Pusat', 'Pluit', 
        'Kuningan', 'Pluit'] '''
    ''' implement Leidner Spatial Minimality (2008) & SMCD Centroid Distance '''
    print("|disambiguating document based on: ",toponyms)
    #toponyms = list ( set (toponyms) )

    global PROD

    global polygon_pts
    T = []
    toponyms = list ( set (toponyms) )
    total = 1
    ALLT = [ ambigus(t) for t in toponyms ]
    ALLT = [ item for item in ALLT if len(item) > 0 ]

    if (algorithm == "smcd-adm"):
        T = [list_places for list_places in ALLT if len(list_places) > 1]
        SINGULAR = [list_places for list_places in ALLT if len(list_places) == 1]
        print ("T=",T)
        print ("SINGULAR=", SINGULAR)
    else:
        T = ALLT
        
    if verbosity >= 2 : print ("producing combinations")        
    PROD = product(*T)
    winning = ()
    min_area = sys.float_info.max
    first_tuple = None
    if verbosity >= 2 : print ("total", total)
    print ("algorithm = ", algorithm)
    
    if len(T) > 0 :
        num = 1
        for tupl in PROD:
            num = num + 1
            if verbosity >= 3 :
                print ("tupl", tupl)
                if num % 10000 == 0:
                    print (100.0 * num / total)
            if verbosity >= 3 : print (tupl)
            if first_tuple is None: first_tuple = tupl
            
            admin_pts = []
            # create the list of points from tupl
            polygon_pts = []
            for p in tupl:
                ll = latlng(p)
                adm = int( get_admlevel(p) )
                if ll: 
                    polygon_pts.append( ll )
                    admin_pts.append( adm )
                    
                    
            #print(polygon_pts)
    
            # heuristic one sense per discourse (OSPD)
            if verbosity >= 4 : print("filtering points from", len(polygon_pts))
            polygon_pts = list(set(polygon_pts)) # discard same points
            if verbosity >= 4 : print("filtering points to", len(polygon_pts))
            
            if algorithm == "smcd-adm":
                poly_area = findmaxdist_adm(polygon_pts, admin_pts)
    
            elif algorithm == "smcd":  #spatial minimality based on max centroid distance 
                poly_area = findmaxdist(polygon_pts)
                
            else: #regular spatial minimality based on area'''
                if len(polygon_pts) < 3: # hack if polygon is less than 2 points.
                    if verbosity >= 3: 
                        print ("insufficient points")
                    return first_tuple # first tuple wins
                poly_area = findarea(polygon_pts)
                if verbosity >= 3: 
                    print ("polygon_pts", polygon_pts)
            #print (tupl, "area", poly_area)
            if verbosity >=3:
                print ("--", tupl, "\narea", poly_area)
            if poly_area < min_area:
                if verbosity >=3:
                    print ("***")
                winning = tupl
                min_area = poly_area
    print ("|winner = ", winning)
    if (algorithm == "smcd-adm"):
        for s in SINGULAR:
            winning = winning + tuple([s[0]])
        return winning
    else:
        return winning
            

def disambiguate_document_v1(toponyms, algorithm = "smcd"):
    ''' toponyms are list of t in document, ex [
        'Jakarta', 'Jakarta Pusat', 'Pluit', 
        'Kuningan', 'Pluit'] '''
    ''' implement Leidner Spatial Minimality (2008) & SMCD Centroid Distance '''
    print("|disambiguating document based on: ",toponyms)
    #toponyms = list ( set (toponyms) )

    global PROD
    global T
    global polygon_pts
    T = []
    toponyms = list ( set (toponyms) )
    total = 1
    ALL = [ ambigus(t) for t in toponyms ]
    T = [list_places for list_places in ALL if len(list_places) > 1]
    SINGULAR = [list_places for list_places in ALL if len(list_places) == 1]
        
    if verbosity >= 2 : print ("producing combinations")        
    PROD = product(*T)
    winning = None
    min_area = sys.float_info.max
    first_tuple = None
    if verbosity >= 2 : print ("total", total)
    
    num = 1
    for tupl in PROD:
        num = num + 1
        if verbosity >= 3 :
            if num % 10000 == 0:
                print (100.0 * num / total)
        if verbosity >= 3 : print (tupl)
        if first_tuple is None: first_tuple = tupl
        
        # create the list of points from tupl
        polygon_pts = []
        for p in tupl:
            ll = latlng(p)
            if ll: polygon_pts.append( ll )
        #print(polygon_pts)

        # heuristic one sense per discourse (OSPD)
        if verbosity >= 3 : print("filtering points from", len(polygon_pts))
        polygon_pts = list(set(polygon_pts)) # discard same points
        if verbosity >= 3 : print("filtering points to", len(polygon_pts))
        

        if algorithm == "smcd":  #spatial minimality based on max centroid distance 
            poly_area = findmaxdist(polygon_pts)
        else: #regular spatial minimality based on area'''
            if len(polygon_pts) < 3: # hack if polygon is less than 2 points.
                if verbosity >= 3: 
                    print ("insufficient points")
                return first_tuple # first tuple wins
            poly = cons_poly2 ( polygon_pts )
            poly_area = area(poly)
        #print (tupl, "area", poly.area)
        if verbosity >=3:
            print ("--", tupl, "area", poly_area)
        if poly_area < min_area:
            if verbosity >=3:
                print ("***")
            winning = tupl
            min_area = poly_area
    print ("|winner = ", winning)

    for s in SINGULAR:
        winning = winning + tuple([s[0]])
    return winning
            
    
def cons_polygon(pts):
    if len(pts)<3:
        print("polygon needs >=3 pts")
        return None
    else:
        pol = Polygon(pts)
        return pol
    

def cons_poly2(pts):
    if len(pts)<3:
        print("polygon needs >=3 pts")
        return None
    else:
        obj = {'type':'Polygon','coordinates':[[ [ X[0], X[1]] for X in pts ]]}
        return obj
    
latlng_re = re.compile(".*\((.*\,.*)\)")

def scale(factor, ll):
    return (ll[0]* factor, ll[1]* factor)

def latlng(fullname):
    m = latlng_re.match(fullname)
    if m:
        ll = m.group(1).strip().split(',')
        return ( float(ll[0]), float(ll[1]) )
        
    else:
        return None
    
def getField(code, word_object):
    '''
    
    '''
    if type(word_object) == dict:
        return word_object[fieldname]
    else:
        if fieldname == "world.lower()":
            return word_object


def disambiguate_document_sm(sents, algorithm = "smcd-adm"):
    ''' disambiguating based on spatial minimality 
    (sents is sentences from one single document to be disambiguated)
    sents will be piggybacked with the adm level for each of the toponym found.
       
    '''
    global verbosity
    global toponyms_map
    global toponyms 
    
    toponym_idx = 0
    toponyms = [] # document-level toponyms separated by ===
    toponyms_map = []

    
    print ("disambiguating list of toponyms")
    sentidx = 0
    for sent in sents:
        #print ("---")
        startCollect = False
        toponym = []
        widx = 0
        widx_start = 0
        for w in sent:
            ''' dict:
                word.lower()
                word.event
                word.geo
                word.arg
                word.entity   
            '''
            #print(line)
            EOL = sent.index(w) == len(sent) - 1
            #if EOL: print ("EOL")

            if startCollect:
                if w[2] == 'I-LOC' or w[2] == "I-PLOC" and not EOL: #inside the LOC
                    toponym.append( w[0] )
                    
                    #print("append2", line[0] )
                else: # finished collecting, change from B-I to O or to another B or EOL
                    if verbosity >= 2:
                        print ("EOL" if EOL else "")
                        print ('-',w[2],w[0])

                    if EOL :
                        #print("append3", line[0] )
                        toponym.append( w[0] )
                        
                    toponym_found = ' '.join(toponym)
                    print ("*", toponym_found)

                    toponym_idx = toponym_idx + 1
                    #print_ambiguations( ambigus(toponym_found) )
                    toponyms.append( toponym_found )
                    toponyms_map.append((sentidx, widx_start)) # the sentence index and word index start of B-LOC segment for this toponym
                    
                    #r = find_ambigus(toponym_found)
                    #print_ambigus(r)
                    startCollect = False
                    loc = None
                    toponym = []
                    #now it's time to disambiguate that toponym
            if w[2] == 'B-LOC' or w[2] == "B-PLOC":
                 #start collecting tokens
                
                #loc = w[3] #the coordinate -> this can only be looked up later
                #locs.append (loc)
                #print("LOC FOUND", loc)
                startCollect = True
                widx_start = widx
                toponym.append( w[0] )
 
                
                if EOL:
                    #print("append3", line[0] )
                    
                    toponym_found = ' '.join(toponym)
                    print ("*", toponym_found)

                    toponym_idx = toponym_idx + 1
                    #print_ambiguations( ambigus(toponym_found) )
                    toponyms.append( toponym_found )
                    toponyms_map.append((sentidx, widx_start)) # the sentence index and word index start of B-LOC segment for this toponym
                    
                    #r = find_ambigus(toponym_found)
                    #print_ambigus(r)
                    startCollect = False
                    loc = None
                    toponym = []
                #print("startcollect")
            widx = widx + 1
        sentidx = sentidx + 1
    #toponyms = filter_duplicate_toponyms( toponyms ) 
    #if len(toponyms) < 15: # cutoff due to exponential algorithm
    f_toponyms = list(set(toponyms))
    f_toponyms = f_toponyms[:15]
    winner = disambiguate_document( f_toponyms )
    
    
    max_adm_lvl = 0
    global toponyms_admlvl
    toponyms_admlvl = {}
    global toponyms_disambiguated
    toponyms_disambiguated = {}
    
    #first we find max adm level
    for idx, t in enumerate(toponyms):
        r = ambigus(t)
        for fullname in winner:
            if fullname in r:
                print ('|predicted disambiguated value of',t,'=', fullname  )
                print (toponyms_map[idx])
                
                adm_lvl = int(get_admlevel(fullname))
                if adm_lvl > max_adm_lvl :
                    max_adm_lvl = adm_lvl
                toponyms_admlvl [ toponyms_map[idx] ] = adm_lvl # for indexing the adm lvl
                toponyms_disambiguated [ toponyms_map[idx] ] = fullname
                
                
    print("max adm level", max_adm_lvl)
    
    #then we modify the ismax (Smallest Administrative Level) field
    for idx, t in enumerate(toponyms):        
        print (toponyms_map[idx])
        sentidx = toponyms_map[idx][0]
        widx = toponyms_map[idx][1]
        length = len(t.split())
        print(t)
        for i in range(0, length):
            #sents[sentidx][widx]["word.ismax"] = ( toponyms_admlvl [ (sentidx, widx) ] == max_adm_lvl )
            
            try:
                if verbosity >= 1:
                    ''' patch the admlvl'''
                    print("patching sents t", t, sentidx, widx, toponyms_admlvl [ (sentidx, widx) ])
             
                sents[sentidx][widx][6] = ( toponyms_admlvl [ (sentidx, widx) ] )
                sents[sentidx][widx][7] = ( toponyms_admlvl [ (sentidx, widx) ] == max_adm_lvl )
                sents[sentidx][widx][8] = toponyms_disambiguated[ (sentidx, widx) ]
                
            except:
                pass
    locs = []
    



def disambiguate_trainingset( noploc = True, algorithm = "smcd-adm" ):
    global total_pred
    global correct_pred
    total_pred = 0
    correct_pred = 0
    w = ""
    locs = []
    toponyms = []
    def b():
        locs.append(w[3])
        return
    def c():
        toponyms.append(' '.join(bio.chunk))
        return
    
    bio = BIO(b,c)
    sents = load_annotation("G:/Riset/Gatotkaca/Exp06-Extraction/"+dataset_folder+"/training.txt", noploc = noploc )
    for sent in sents:
        for w in sent:
            if w == "===" or w == "=":
                bio.next("","$")
                winner = disambiguate_document( toponyms[:10], algorithm )
                evaluate_winner(winner, toponyms, locs)
                toponyms = []
                locs = []
                bio.next("","^")
                bio.reset()
            else:
                #print("w is",w)
                if w[2][-3:]=="LOC":
                    bio.next(w[0],w[2][0])
                    if verbosity >= 3:
                        print("w is",w)
                else:
                    bio.next(w[0],"O")
    print("total pred", total_pred)
    print("correct pred", correct_pred)
    print("acc", correct_pred / total_pred)
            
            
    
def disambiguate_list_sm( noploc = True, algorithm = "smcd-adm" ):
    ''' 
    disambiguating training set 
    list based on spatial minimality (sm) or spatial min centroid distance (smcd) 
    this is deprecated! 
       
    '''

    global total_pred
    global correct_pred
    global sents
    total_pred = 0
    correct_pred = 0
    toponyms = [] # document-level toponyms separated by ===
    locs = []

    if algorithm == "smcd-ploc" :
        if noploc :
            print ("for smcd-ploc algorithm, noploc must be False")
            return False
        
    print ("disambiguating list of toponyms")
    sents = load_annotation("G:/Riset/Gatotkaca/Exp06-Extraction/"+dataset_folder+"/training.txt", noploc = noploc )
    print ("using default annotation")
    for sent in sents:
        #print ("---")
        startCollect = False
        toponym = []
        
        for w in sent:
            ''' there are 2 possible value of w
            1. scalar ===/= (end of doc)
            2. list, ex: 
                   1          2       3                 4
                ['Pejaten', 'NNP', 'B-LOC', '(-6.272953462733, 106.83516677480338)', 'Place-Arg']
                This is the first evolution that read directly sents from file.
            '''
            
            if w == "===" or w == "=": # end of document
                if verbosity >= 1:
                    print("end of document")
                #toponyms = filter_duplicate_toponyms( toponyms ) 
                
                
                toponyms = toponyms[:15]
                #if len(toponyms) < 15: # cutoff due to exponential algorithm
                winner = disambiguate_document( toponyms, algorithm ) 
                # winner is the winning tuple in the document
                # toponyms is the toponym list in the document
                # locs is the correct coordinate obtained from 4th field inside annotation file
                # the evaluation is done at the end of document as the spatial minimality works for each doc level.
                evaluate_winner(winner, toponyms, locs)
            
                toponyms = []
                locs = []


            #print(line)
            EOL = sent.index(w) == len(sent) - 1
            #
            if verbosity >= 2:
                print ("EOL" if EOL else "")
                print ('-',w[2],w[0])

                #print("startcollect")

            if startCollect:
                if w[2] == 'I-LOC' or w[2] == 'I-PLOC' and not EOL: #begin or inside the LOC
                    toponym.append( w[0] )
                    if verbosity >= 2:
                        print ('append',w[0])
                    #print("append2", line[0] )
                else: # finished collecting, change from B-I to O or to another B or EOL
                    if verbosity >= 2:
                        print ('finish collecting')
                    if EOL :
                        #print("append3", line[0] )
                        toponym.append( w[0] )
                        
                    toponym_found = ' '.join(toponym)
                    print ("*", toponym_found)

                    if verbosity >= 3:
                        print_ambiguations( ambigus(toponym_found) )
                    toponyms.append( toponym_found )
                   
                    #r = find_ambigus(toponym_found)
                    #print_ambigus(r)
                    startCollect = False
                    loc = None
                    toponym = []
                    continue
                    #now it's time to disambiguate that toponym
            if w[2] == 'B-LOC' or w[2] == 'B-PLOC' :
                 #start collecting tokens
                if w[0].lower() == "jl" or w[0].lower() == "jalan": continue
                # append the location lat long
                loc = w[3]
                locs.append (loc)

                toponym.append( w[0] )
                #print("LOC FOUND", loc)
                startCollect = True
                if verbosity >= 2:
                    print ('start collect append',w[0])
                continue

    print("total pred", total_pred)
    print("correct pred", correct_pred)
    print("acc", correct_pred / total_pred)

# kalau outputnya O/O maka pasti error.
def predict(input_str, algorithm="smcd-adm"):
    global X_ploc
    global X_all
    global X_event
    global X_arg
    global X_entity
    global X
    
    global total_sents
    global sent_idx


    global y_arg
    global y_event
    global y_entity
    global y_ploc
    global sents
    global crf_event, crf_entity

    #to assist some tokenization of ina nlp

    # kata Joko.Sehingga => kata Joko. Sehingga

    input_str = re.sub("\.([a-zA-Z\"])", ". \g<1>",input_str)


    # transform datefield dd/mm/yyyy to dd*mm*yyy so inanlp can process it well

    input_str = re.sub("\(([0-3]?[0-9])/([0-1]?[0-9])/(\d\d\d?\d?)\)", "( \g<1>:\g<2>:\g<3> )", input_str) # full date

    input_str = re.sub("\(([0-2]?[0-9])/([0-1]?[0-9])\)", "( \g<1>:\g<2> )", input_str) # dd mm

    input_str = re.sub("([a-zA-Z])\,", "\g<1> , ", input_str)

    input_str = postag(input_str)

    # retransform and put DD code
    #input_str = re.sub("([0-3]?[0-9])\:([0-2]?[0-9])\:([1-2]?[0-9]?[0-1][0-9])/[A-Z][A-Z][A-Z]?", "\g<1>/\g<2>/\g<3>/DD", input_str) #dd mm yy/yyyy only

    #input_str = re.sub("([0-2]?[0-9])\:([0-1]?[0-9])\:[A-Z][A-Z][A-Z]?", "\g<1>/\g<2>/DD", input_str) #dd and mm only

    doc = re.split('\r\n|\n|\.', input_str)
    i = 1
    clean = []
    for _line in doc:
        print(_line)
        if (_line.find('{/NN') != -1):
            clean.append('****')
        elif (_line.find('{') != -1):
            clean.append(_line)
        elif i%2 == 0:
            clean.append(_line)

        i = i + 1

    clean2 = [breakwords(l) for l in clean if (l.find("****")==-1 and l.find("{") == -1) and len(l)>1 ]
    
    with open("temp.txt", 'w', encoding="utf8") as fo:
        for doc in clean2:
            fo.write("\n".join(doc))
        fo.write("===")
    
    sents = load_annotation("temp.txt", stripdocs= True, predictMode = True)
    total_sents = len(sents)
    sent_idx = 0

    mode = "entity"
    
    X = [sent2features(s, mode) for s in sents]
    y = [sent2labels(s, mode) for s in sents]
    X_entity = X.copy()
    y_entity = crf_entity.predict(X)
    
    # pass the entity codes
    for sentidx, sent in enumerate(sents):
        for widx, w in enumerate(sent):
            try:
                sents[sentidx][widx][2] = y_entity[sentidx][widx]
            except:
                pass
            
    mode = "event" #second predict, event mode
    X = [sent2features(s, mode) for s in sents]
    y = [sent2labels(s, mode) for s in sents]
    if 'entity' in event_options:
        for ix, sent in enumerate(y_entity):
            for iy, entity in enumerate(sent):
                X[ix][iy]["word.entity"] = entity
                if iy > 0:
                    X[ix][iy]["-1:word.entity"] = sent[iy-1]
                if iy < len(sent) - 1:
                    X[ix][iy]["+1:word.entity"] = sent[iy+1]
    X_event = X.copy()
    y_event = crf_event.predict(X)

    mode = "arg" #3rd predict, arg mode
    X = [sent2features(s, mode) for s in sents]
    y = [sent2labels(s, mode) for s in sents]
    if 'entity' in arg_options:
        for ix, sent in enumerate(y_entity):
            for iy, entity in enumerate(sent):
                X[ix][iy]["word.entity"] = entity
                if iy > 0:
                    X[ix][iy]["-1:word.entity"] = sent[iy-1]
                if iy < len(sent) - 1:
                    X[ix][iy]["+1:word.entity"] = sent[iy+1]
                    
    if 'event' in arg_options:
        for ix, sent in enumerate(y_event):
            for iy, event in enumerate(sent):
                X[ix][iy]["word.event"] = event
                if iy > 0:
                    X[ix][iy]["-1:word.event"] = sent[iy-1]
                if iy < len(sent) - 1:
                    X[ix][iy]["-1:word.event"] = sent[iy+1]
    X_arg = X.copy()
    y_arg = crf_arg.predict(X)
    
    mode = "ploc" #4th predict, event mode
    
    disambiguate_document_sm( sents, algorithm ) # disambiguate document will piggyback the recognized toponyms with administrative lev and ismax (smallest administrative level ) feature
    
    X = [sent2features(s, mode) for s in sents]
    y = [sent2labels(s, mode) for s in sents]
    
    if 'event' in ploc_options:
        print("merge the X_test's word.event feature using y_pred from previous train arg and event session")
        for ix, sent in enumerate(y_event):
            for iy, event in enumerate(sent):
                X[ix][iy]["word.event"] = event
                if iy > 0:
                    X[ix][iy]["-1:word.event"] = sent[iy-1]
                if iy < len(sent) - 1:
                    X[ix][iy]["-1:word.event"] = sent[iy+1]
    if 'arg' in ploc_options:                
        for ix, sent in enumerate(y_arg):
            for iy, arg in enumerate(sent):
                X[ix][iy]["word.arg"] = arg
                if iy > 0:
                    X[ix][iy]["-1:word.arg"] = sent[iy-1]
                if iy < len(sent) - 1:
                    X[ix][iy]["-1:word.arg"] = sent[iy+1]
                    
    if 'entity' in ploc_options:
        for ix, sent in enumerate(y_entity):
            for iy, entity in enumerate(sent):
                X[ix][iy]["word.entity"] = entity
                if iy > 0:
                    X[ix][iy]["-1:word.entity"] = sent[iy-1]
                if iy < len(sent) - 1:
                    X[ix][iy]["+1:word.entity"] = sent[iy+1]
                    
    X_ploc = X.copy()    
    y_ploc = crf_ploc.predict(X)
    
    for ix, sent in enumerate(y_ploc):
            for iy, ploc in enumerate(sent):
                X[ix][iy]["ploc"] = ploc

    
    X_all = merge( X_entity, X_event, X_arg, X_ploc )
    display(X_all, y_entity, y_event, y_arg, y_ploc)
    
def merge(X1,X2,X3,X4):
    for ix, sent in enumerate(X1):
        for iy, w in enumerate(sent):
            X1[ix][iy] = {**X1[ix][iy],**X2[ix][iy],**X3[ix][iy],**X4[ix][iy]}
    return X1

printline = []

def getdisambiguated(idxsent,idxw):
    try:
        return toponyms_disambiguated[ (idxsent, idxw) ]
    except KeyError:
        print ("getdisambiguated error ", idxsent, idxw)
        return ""
    
def display (X, y_entity, y_event, y_arg, y_ploc, fileout=None):
    ''' display predicted result 


    '''
    global printline

    printline = []
    for idxsent, sent in enumerate(X):
        for idxw, w in enumerate(sent):
            if verbosity == 2: 
                print(w)
            if w["word.istitle()"]:
                w["word.lower()"] = w["word.lower()"].capitalize()
            elif w["word.isupper()"]:
                w["word.lower()"] = w["word.lower()"].upper()
            w["word.arg"] = y_arg[idxsent][idxw]
            w["word.event"] = y_event[idxsent][idxw]
            w["ploc"] = y_ploc[idxsent][idxw]
            printline.append({
                    "word":w["word.lower()"], 
                    "entity":w["word.entity"], 
                    "arg":w["word.arg"], 
                    "ploc":w["ploc"], 
                    "postag":w["postag"], 
                    "event":w["word.event"],
                    "disambiguated": getdisambiguated(idxsent,idxw),
                    "index": (idxsent, idxw)
                    })
            

    fbuffer = []
    for w in printline:

            #       1                2                  3                   4                   5                6
        line = w["word"]+ "/"+ w["postag"] + "/" + w["entity"] + "/" + w["event"] + "/" + w["arg"] + "/" + w["ploc"] + "/" + w["disambiguated"]

        print (line)
        fbuffer.append(line)
        

    if fileout:
        with open(fileout, 'w', encoding='utf8') as fo:
            fo.write("\n".join(fbuffer))
    
    visualize()
    

    
def collect(entity, mode, value = ''):
    
    '''     To collect all entities that has the 'entity' type which mode = 'mode' and which mode value = value.
            examples:
                    1. collecting all argument values of Height-Arg
                        collect('ARG', 'arg', 'Height-Arg')
                    2. collecting all event triggers entity 
                        collect('EVE', 'entity')
                    3. collecting all inferred event
                        collect('EVE','event')
                    4. collecting all disambiguated loc (not ploc)
                        collect('LOC','ploc','LOC')
                    
            available entity: 
                EVE, ARG, ORG, LOC
            available mode:
                entity, event, arg, ploc, disambiguated
            available values
                depends on mode, 
                if mode = arg can be Height-Arg, Place-Arg etc.
                if mode = entity this value should not be filled.
                if mode = event can be FLOOD-EVENT, FIRE-EVENT etc
                if mode = ploc can be LOC or PLOC.
                
            return values:
                return value are list of pair (tuple) of the entity extracted
                and the position (sentence index, wordindex) in the doc. 
                and the disambugated fullname (if the LOC is requested)
    '''
    ents = []
    prev_ent = ''
    ent = []
    startCollect = False
    for widx,w in enumerate(printline):
        
            EOL = widx == len(printline) - 1
            if w["entity"] == "B-"+ entity and (value == w[mode] or value == ''):
                startCollect = True
                startIdx = w["index"]
                startDisambiguated = w['disambiguated']
            if startCollect:
                if ((w["entity"] == "I-" + entity) or (w["entity"] == "B-" + entity)) and not EOL and (value == w[mode] or value=='') :
                    ent.append( w['word'] )

                else:# finished collecting, change from B-I to O or to another B or EOL
                    if EOL:
                        ent.append (w['word'])
                    ent_found = ' '.join(ent)
                    ent = []
                    startCollect = False
                    if entity == "LOC":
                        ents.append ((ent_found, startIdx, startDisambiguated))
                    else:
                        ents.append ((ent_found, startIdx))
                
    return ents
                
def parseNumbers(strNum):
    ''' parse the numbers found in the sentences '''
    return re.findall('\d+', strNum )

def ave(l):
    l = [int(si) for si in l]
    return sum(l) / len(l)
    
def match_entities(gpd_t, locs, args):
    for arg in args:
        ''' match with respective sentence index '''
        arg_sidx, arg_widx = arg[1]
        
        for loc in locs:
            
            loc_sidx, loc_widx = loc[1]

            if loc_sidx == arg_sidx : 
                ''' there is argument and loc at same sentence. '''
                print ("match",arg[0], "at", loc[0])

                fullname = loc[2].split("(")[0] # strip the coordinate
                uid = geocode(fullname, return_uid = True)
                if (uid):
                    val = ave(parseNumbers(arg[0]))
                    print("set", arg[0], loc[0], val)
                    setval(gpd_t, uid, val)
                
                
def setval(gpd_t, uid, val):
    gpd_t.at[uid, "value"] = val
    
def visualize():
    global DKI_UID
    #DKI_UID = ALL.query('NAME_1 == "Jakarta Raya"').set_index('UID')
    DKI_UID = ALL.query('NAME_2 == "Jakarta Timur" or NAME_2 == "Jakarta Selatan"').set_index('UID')
    DKI_UID["value"] = 0
    
    water = gpd.read_file('..\Exp-16-Geonames\waterways.geojson')
    
    
    locs = collect('LOC','ploc','LOC')
    args = collect('ARG', 'arg', 'Height-Arg')
    match_entities(DKI_UID, locs, args)
    plots(DKI_UID)



def plots(gpd_t):  
    ax = gpd_t.plot(column='value', cmap='OrRd', figsize=(10,10), edgeColor="black")
    gpd_t.apply(lambda x: ax.annotate(s=x.NAME_4, fontsize=7, xy=x.geometry.centroid.coords[0], ha='center'),axis=1);
    return ax


    
def plots2(gpd_t):  
    gpd_t = gpd_t.to_crs(water.crs)
    ax = gpd_t.plot(column='value', cmap='OrRd', figsize=(10,10), edgeColor="black")
    water.plot( ax = ax,  color='blue')
    gpd_t.apply(lambda x: ax.annotate(s=x.NAME_4, fontsize=10, xy=x.geometry.centroid.coords[0], ha='center'),axis=1);
    return ax

def train():
    train_crf(mode='entity')
    train_crf(mode='event')
    train_crf(mode='arg')
    train_crf(mode='ploc')

    
#load_crf()


#train()
    



# in order to evaluate toponym resolution result from small corpus
#disambiguate_trainingset(algorithm="sm")
#disambiguate_trainingset(algorithm="smcd")
#disambiguate_trainingset(algorithm="smcd-adm")
#%%

def ablation(_mode = 'entity'):
# perform the ablation test for each of the four steps / modes in geoparsing.
# This is only for the research, not required for using the geoparser.
    global ploc_options
    global event_options
    global arg_options
    global entity_options
    
    params = [
            ('',['entity','event','arg','ploc']), #1
            ('gaz',['entity','event','arg','ploc']), #2
            ('gaz|postag',['entity','event','arg','ploc']), #3
            ('org_regex|gaz|postag',['entity','event','arg','ploc']), #4
            ('org_regex|arg_regex|gaz|postag',['entity','event','arg','ploc']), #5
            ('org_regex|arg_regex|ev_keywords|gaz|postag',['entity','event','arg','ploc']),#6
            ('ev_keywords',['entity','event','arg','ploc']),  #7
            ('ev_keywords|gaz|postag',['entity','event','arg','ploc']),  #8
            ('ev_keywords|gaz|postag|entity',['event','arg','ploc']),  #9
            ('arg_regex|ev_keywords|gaz|postag|entity',['event','arg','ploc']),  #10
            ('ev_keywords|entity',['event','arg','ploc']),  #11
            ('entity|event',['arg','ploc']), #12
            ('org_regex|arg_regex|ev_keywords|gaz|postag|entity',['event','arg','ploc']), #13
            ('org_regex|arg_regex|ev_keywords|gaz|postag|entity|event',['arg','ploc']), #14
            ('ev_keywords|gaz|entity|event',['arg','ploc']), #15
            ('ev_keywords|gaz|entity|event|arg',['ploc']), #16
            ('ev_keywords|gaz|entity|event|arg|ismax',['ploc']), #17
            ('arg_regex|ev_keywords|gaz|entity|event|arg|ismax',['ploc']), #18
            ('org_regex|arg_regex|ev_keywords|gaz|entity|event|arg|ismax',['ploc']), #19
            ('ismax',['ploc']),#20
            ('ismax|arg',['ploc']),#21
            ('ismax|arg|event',['ploc']), #22 --> best
            ('ismax|arg|entity|event',['ploc']), #23
            
            ]
    
    for idx, (opt, mode_allowed) in enumerate(params):
        print("testing #", idx + 1, " options = ", opt)
        if _mode in mode_allowed:
            if _mode=="entity":
                entity_options = opt
            elif _mode == "event":
                event_options = opt
            elif _mode == "arg":
                arg_options = opt
            elif _mode == "ploc":
                ploc_options = opt
            train_crf(mode=_mode, cross_validation=False)
        else:
            print("skipping option ", opt, " in ", _mode)
    
if __name__ == '__main__':
    print("event geoparser v.0.1")


