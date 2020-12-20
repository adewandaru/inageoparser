# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 09:38:03 2019

@author: dewandaru@gmail.com
"""
import geopandas as gpd 
import pandas as pd
import re 

from globalmod import *

#L0 = 
#L1 = gpd.read_file('D:\Riset\Gatotkaca\Exp-16-Geonames\gadm36_USA_shp\gadm36_USA_1.shp')
#L2 = gpd.read_file('D:\Riset\Gatotkaca\Exp-16-Geonames\gadm36_USA_shp\gadm36_USA_2.shp')

print("load")


print("..loading global GADM database...")
ALL = gpd.read_file('..\gadm36_shp\gadm36.shp')
NAME0 = ALL.set_index('NAME_0')
NAME1 = ALL.set_index('NAME_1')
NAME2 = ALL.set_index('NAME_2')
NAME3 = ALL.set_index('NAME_3')
NAME4 = ALL.set_index('NAME_4')
NAMES = [NAME0, NAME1, NAME2, NAME3, NAME4]

COUNTRIES = []
COUNTRIES = pd.read_csv(r"translations\COUNTRIES-ID.csv")  
COUNTRIES = COUNTRIES.set_index('ID')

US = pd.read_csv("uscities.csv")
US = US.set_index("city")

__geospatial__ = True

print("GADM database loaded.")

def reload():
    global ALL
    global NAME0,NAME1,NAME2,NAME3,NAME4,NAME5
    global US
    global COUNTRIES
    print("reloading global GADM database...")
    ALL = gpd.read_file('gadm36_shp\gadm36.shp')
    NAME0 = ALL.set_index('NAME_0')
    NAME1 = ALL.set_index('NAME_1')
    NAME2 = ALL.set_index('NAME_2')
    NAME3 = ALL.set_index('NAME_3')
    NAME4 = ALL.set_index('NAME_4')
    NAMES = [NAME0, NAME1, NAME2, NAME3, NAME4]

    COUNTRIES = []
    COUNTRIES = pd.read_csv(r"..\translations\COUNTRIES-ID.csv")  
    COUNTRIES = COUNTRIES.set_index('ID')
    
    US = pd.read_csv("uscities.csv")
    US = US.set_index("city")
    

def pplot2(gpd_t):   
    ax = gpd_t.plot(column='value', cmap='OrRd', figsize=(30,30))
    gpd_t.apply(lambda x: ax.annotate(s=x.name, fontsize=7, xy=x.geometry.centroid.coords[0], ha='center'),axis=1);

def value(fullname, val):
    r = DKI.loc[label]        
    DKI.at[label,"value"] = val
    
# convert indonesian names to international one.
def to_intl(t):
    try: 
        return COUNTRIES.loc[t].INTL
    except: 
        return t

def point( place ):
    return ""
    return "[" + str(place.geometry.centroid.x) + "," + str(place.geometry.centroid.y) + "]"
    
    
def join( lst ):
    return ",".join( lst )
    
def append(ambigus, lvl, t, place):
    if lvl == 4 : # desa level
        ambigus.append( join ( ['Village/Desa/Kel:'+ t, place.NAME_3, place.NAME_2, place.NAME_1, place.NAME_0 ] ) )
    elif lvl == 3:
        ambigus.append( join ( ['Subdistrict/Kec:'+ t, place.NAME_2, place.NAME_1, place.NAME_0 ] ) )
    elif lvl == 2:
        ambigus.append( join ( ['City/Kota/Kab:'+ t, place.NAME_1, place.NAME_0 ] ) )
    elif lvl == 1:
        ambigus.append( join ( ['Province:'+ t, place.NAME_0] ) )
    elif lvl == 0:    
        ambigus.append( join ( ['Country:'+ t] ) )
        
''' special for US cities '''    
def append_us(ambigus, t, place):
    ambigus.append( join ( ['City:'+ t, place.state_name, "United States" ] ) )        
    
''' special for Indo names'''    
def append_other(ambigus, t, place):
    print(place)
    ambigus.append( place[0] )    
        
SUBS = {

    "Kepri":["Kepulauan Riau"],
    "Bandung":["Kota Bandung","Bandung"],
    "Baru":["Kota Baru"],
    "Bekasi":["Bekasi","Kota Bekasi"],
    "Bima":["Bima","Kota Bima"],
    "Binjai":["Binjai","Kota Binjai"],
    "Blitar":["Blitar","Kota Blitar"],
    "Bogor":["Bogor","Kota Bogor"],
    "Cirebon":["Cirebon","Kota Cirebon"],
    "DKI Jakarta":["Jakarta Raya"],
    "Gorontalo":["Kota Gorontalo","Gorontalo"],
    "Jakarta":["Jakarta Raya"],
    "Jayapura":["Kota Jayapura","Jayapura","Jaya Pura"],
    "Kediri":["Kediri","Kota Kediri"],
    "Kupang":["Kupang","Kota Kupang"],
    "Madiun":["Madiun","Kota Madiun"],
    "Magelang":["Magelang","Kota Magelang"],
    "Malang":["Malang","Kota Malang"],
    "Medan":["Kota Medan"],
    "Mojokerto":["Mojokerto","Kota Mojokerto"],
    "Padang Sidempuan":["Padangsidimpuan"],
    "Pasuruan":["Pasuruan","Kota Pasuruan"],
    "Pekalongan":["Pekalongan","Kota Pekalongan"],
    "Pematang Siantar":["Pematangsiantar"],
    "Probolinggo":["Probolinggo","Kota Probolinggo"],
    "Semarang":["Semarang","Kota Semarang"],
    "Solok":["Solok","Kota Solok"],
    "Sorong":["Sorong","Kota Sorong"],
    "Sukabumi":["Sukabumi","Kota Sukabumi"],
    "Tangerang":["Kota Tangerang","Tangerang"],
    "Tanjungbalai":["Kota Tanjungbalai"],
    "Tasikmalaya":["Tasikmalaya","Kota Tasikmalaya"],
    "Tegal":["Tegal","Kota Tegal"],
    "Yogyakarta":["Yogyakarta","Kota Yogyakarta"],
    "DKI":["Jakarta Raya"],
    "DIY":["Yogyakarta"],
    "NTT":["Nusa Tenggara Timur"],
    "NTB":["Nusa Tenggara Barat"],
    "Sumut":["Sumatera Utara"],
    "Sumsel":["Sumatera Selatan"],
    "Sumbar":["Sumatera Barat"],
    "Sulut":["Sulawesi Utara"],
    "Sultra":["Sulawesi Tenggara"],
    "Sulteng":["Sulawesi Tengah"],
    "Sulsel":["Sulawesi Selatan"],
    "Malut":["Maluku Utara"],
    "Kaltim":["Kalimantan Timur"],
    "Kalteng":["Kalimantan Tengah"],
    "Kalsel":["Kalimantan Selatan"],
    "Kalbar":["Kalimantan Barat"],
    "Jatim":["Jawa Timur"],
    "Jateng":["Jawa Tengah"],
    "Jabar":["Jawa Barat"],
    "AS":["Amerika Serikat"],
    "Jakpus":["Jakarta Pusat"],
    "Jakbar":["Jakarta Barat"],
    "Jaksel":["Jakarta Selatan"],
    "Jaktim":["Jakarta Timur"],
    "Jakut":["Jakarta Utara"],
    "Lebak Banten":["Lebak","Banten"],
    "Desa Curahkalak":["Curah Kalak"],
    "Betikharjo":["Bektiharjo"],
    "Kuningan":["Kuningan Barat", "Kuningan Timur", "Kuningan"],
    "Mexico City":["Distrito Federal"],
    "Mampang Perapatan":["Mampang Prapatan"],
    "Mampang":["Mampang Prapatan","Mampang"],   
    "Yaernell Hill":["Yarnell"],
    "Yarnell Hill":["Yarnell"],
    "Namche Bazar":["Namche"],
    "Nangroe Aceh Darussalam":["Aceh"],
    "Pulo Gadung":["Pulogadung"],
    "Meruya":["Meruya Utara", "Meruya Selatan"],
    "Malalayang Satu Timur":["Malalayang I Timur"],
    "Malalayang Dua":["Malalayang II"],
    "Sumatra Barat":["Sumatera Barat"],
    "Sumatra Utara":["Sumatera Utara"],
    "Sumatra Selatan":["Sumatera Selatan"],
    "Kampung Dalam":["Kampung Dalam", "V Koto Kampung Dalam"],
    "Waingapu":["Kota Waingapu"],
    "Tambak Rejo":["Tambakrejo"],
    "Pejaten":["Pejaten Barat","Pejaten Timur","Pejaten"],
    "Kota Bambu":["Kelurahan Kota Bambu", "Kota Bambu Utara","Kota Bambu Selatan"],
    "Curahkalak":["Curah Kalak"],
    "Tanjung Umah":["Tanjung Uma"],
    "Jodoh":["Sungai Jodoh"],
    "Bidaracina":["Bidara Cina"],
    "Meonguane":["Melonguane"],
    "Kedamaean":["Kedamean"],
    "Jangkungsumo":["Jangkungsomo"],
    "Balekambang":["Bale Kambang"],
    
    
}

pstrip = re.compile("(^(kelurahan|kecamatan|provinsi|propinsi|kabupaten|kota|kabupeten|desa|kampung|distrik) )", re.IGNORECASE)
qstrip = re.compile("(.*)( county| city)", re.IGNORECASE)

EXCEPTIONS = ['Mexico City', 'Kota Bambu', 'Kampung Melayu', 'Kampung Dalam']
def strip(str):
    if str in EXCEPTIONS :return str
    str = re.sub(pstrip, "", str)
    str = re.sub(qstrip, "\g<1>", str)
    return str
    #input_str = re.sub("\.([a-zA-Z\"])", ". \g<1>",input_str)
    

def ambigus(t):
    if not isinstance(t, str):
        return
    ''' generate ambiguous place names and coordinates '''
    t = strip(t)
    if len(t) == 0:
        return []
    # find substitutes dictionary
    try:
        Q = SUBS[t]
    except:
        Q = [t]
    res = []
    for q in Q:
        R = _ambigus(q)
        for r in R:
            res.append(r)
    #return set(res)
    return res

def getambigus_indonesia():
    uniq1 = set(list( INDONESIA.NAME_1 ))
    uniq2 = set(list( INDONESIA.NAME_2 ))
    uniq3 = set(list( INDONESIA.NAME_3 ))
    uniq4 = set(list( INDONESIA.NAME_4 ))
    alluniq = uniq1 | uniq2 | uniq3 | uniq4
    ambigus_ = []
    for idx, n in enumerate(alluniq):
        try:
            a = ambigus(n)
            if a is not None and len(a) > 5 :
                ambigus_.append(a)
        except:
            pass
            
    with open("ambigus.indonesia.pickle", 'wb') as f:
        pickle.dump(crf_entity, f)
    
def in_tol(t):
    return t in ["Cipali", "Cipularang", "Bocimi", "Purbaleunyi", "Jakarta", 
                 "Jagorawi", "TB", "Simatupang", "Priok", "JORR", "Bandara", 
                 "Cikampek", "Cikapali", "Cijago", "Palikanci", "Soroja", 
                 "Becakayu", "Cisumdawu", "Jabodebek", "Soker", "Dalam", "kota"]
    
    
def save_geocache():
    with open("D:/Riset/Gatotkaca/Exp06-Extraction/geocache.pickle", 'wb') as f:
        pickle.dump(crf, f)
    print("geocache saved")
    
 
def load_geocache():
    global crf
    
    pickle_in = open("D:/Riset/Gatotkaca/Exp06-Extraction/geocache.pickle", "rb")
    GEOCACHE = pickle.load(pickle_in, encoding='latin1')
      
    print("geocache loaded")   
    
GEOCACHE = {}
def in_gaz(t):
    ''' quick lookup whether toponym t exist in gazeteer '''
    # lookup in cache first
    try: 
        return GEOCACHE[t]
    except:
        pass
    
    t = strip(t)
    
    try:
        Q = SUBS[t]
    except:
        Q = [t]
    res = []
    for q in Q:
        if _ingaz(q):
            GEOCACHE[q] = True 
            return True
    GEOCACHE[q] = False
    return False


LOCALNAMES = {
    "Pondok Indah": ["Other:Pondok Indah,Pondok Pinang,Kebayoran Lama,Jakarta Selatan,Jakarta Raya,Indonesia",(-6.2649756,106.7818375)],
    "Puncak": ["Other:Subdistrict/Kec:Cipanas,Cianjur,Jawa Barat,Indonesia", (-6.7028186,106.9902667)]
}

NONAMES = [
    "Kali"
]

    
def _ingaz(t):
    t = to_intl(t)
    if t in NONAMES:
        return False
    
    for x in [0,1,2,3,4]: 
        try:
            place = NAMES[x].loc[t]
            return True
        except:
            pass
    try:
        place = US.loc[t]
        return True
    except:
        return False
    
    try:
        place = LOCALNAMES[t]
        return True
    except: 
        return False
    
    return False
    
def _ambigus(t):
    t = to_intl(t)
    t = t.title()
    ambigus = []
    # x is simply an administrative level.
    for x in [0,1,2,3,4]: 
        #print ( ambigus )
        try:
            place = NAMES[x].loc[t]
        except:
            place = None
        
        if isinstance(place, pd.DataFrame):
            for r in place.iterrows():
                append(ambigus, x, t, r[1])
        elif isinstance(place, pd.Series):
            append(ambigus, x, t, place)
            
    #us city lookup. we are integrating uscities.csv because GADM lacks info on US cities.

    try:

        place = US.loc[t]
    except:
        place = None
        
    try:
        place = LOCALNAMES[t]
    except:
        place = None
       
    if isinstance(place, pd.DataFrame):
        for r in place.iterrows():
            append_us(ambigus, t, r[1])
    elif isinstance(place, pd.Series):
        append_us(ambigus, t, place)
    else:
        if place != None: append_other(ambigus, t, place)
    
    return geocode_set(set(ambigus))

def geocode_set(set_fullnames):
    names = []
    for name in set_fullnames:
        names.append(name + str(geocode(name)))
    return names
    

def centroid_old(df):
    #try:
    if isinstance(df, pd.DataFrame):
        return ( '['+ str(df.centroid.y.mean()) + ',' + str( df.centroid.x.mean()) +']' )
    elif isinstance(df, pd.Series):
        return ( '['+ str( df.geometry.centroid.y ) + ',' + str( df.geometry.centroid.x ) +']' )   
    #except:
    #    print(df)
    
lc = []
def centroid_coords(list_coords):
    global lc
    dx = 0.0
    dy = 0.0
    lc = list_coords
    for (x,y) in list_coords:
        dx = dx + x
        dy = dy + y
    return (dx / len(list_coords), dy / len(list_coords))

lc = []
def centroid_coords2(list_coords):
    global lc
    lc = list_coords
    from shapely.geometry import MultiPoint
    points = MultiPoint([(m[0],m[1]) for m in list_coords])
    return (points.centroid.x, points.centroid.y)
    

import mpu

def findmaxdist_adm( list_coords, list_adm ):
    ''' implements the SpatialMinimality CentroidDistance with Adm .
        the bigger the administrative level, it should be prioritised.
        meaning, the more a tuple has bigger adm level, the more it should be having lesser 'distance'
    
    if verbosity >= 3:
        print ("list_coords", list_coords)
        print ("list_adm", list_adm)
    '''
    (cx, cy) = centroid_coords2(list_coords)
    maxdist = 0
    
    for i, (x,y) in enumerate(list_coords):
        adm_lvl = list_adm[i]
        cdist = (1+adm_lvl) * 100 * mpu.haversine_distance((cx, cy), (x, y))
        if verbosity>=3:
            print("adm_lvl=", adm_lvl, " cdist=", cdist)
        if cdist >= maxdist:
            maxdist = cdist
            (mx, my) = (x, y)
   
    return maxdist    

def findmaxdist(list_coords):
    ''' implements the SpatialMinimality "CentroidDistance" 
    if verbosity >= 3:
        print ("findmaxdist", list_coords)
    '''
    (cx, cy) = centroid_coords2(list_coords)
    maxdist = 0
    
    for (x,y) in list_coords:
        cdist = mpu.haversine_distance((cx, cy), (x, y))
        if cdist >= maxdist:
            maxdist = cdist
            (mx, my) = (x, y)
    if verbosity>=3:
        print ("mx, my, cx, cy, dist", (mx,my), (cx,cy), mpu.haversine_distance((mx, my), (cx,cy)))
    return mpu.haversine_distance((mx, my), (cx,cy))
            
def findarea(list_coords):
    poly = cons_poly2 ( list_coords )
    poly_area = area(poly)
    return poly_area
    
def centroid(df):
    #try:
    if isinstance(df, pd.DataFrame):
        return (df.centroid.y.mean(), df.centroid.x.mean())
    elif isinstance(df, pd.Series):
        return (df.geometry.centroid.y, df.geometry.centroid.x)   

DFCACHE = {}
DFCACHE_UID = {}
def geocode(fullname, returnDf = False, return_uid = False):
    global df
    global DFCACHE_DF
    global DFCACHE
    try: 
        if return_uid == False:
            return DFCACHE[fullname]
        else:
            return DFCACHE_UID[fullname] 
    except:
        pass
    

    # fullname = 'Subdistrict/Kec:Sidoarjo,Sidoarjo,Jawa Timur,Indonesia'
    #                               NAME_3 ...                    NAME_0
    # level                           3         2           1       0
    # parts                           0         1           2       3
    # partslevel's parent = len(parts) - level
    
    if ":" in fullname:
        fullname = fullname.split(":")[1]
    parts = fullname.split(",")
    level = len(parts) - 1
    
    try:  
        if parts[-1]=="United States" and level==2:
            #print('special' , parts[0], parts[1])
            
            df = US.loc[[parts[0]]]
            df = df[ df['state_name'] == parts[1] ]
            #print (df)
            y = float(df.lat)
            x = float(df.lng)
            
        else:
            ''' 
                here we are doing a calculation for finding the centroid of the dataframes matches 
                centroid calc is important because in GADM, the parental dataframes has no specific lat long attached to it.
                instead, it needs to be calculated from all its children.
                
            '''
           # print("level", level)
            df = NAMES[level]
            df = df.loc[[parts[0]]]
            if level > 0:
                # filter dataframes that does not belong to the correct country. this is valid for non country reference.
                # for country we can safely assume that there's no ambiguity.
                
                df = df[ df['NAME_0'] == parts[-1] ] 
                
                parts_parent_str = str(level - 1)
                partslevel_parent = len(parts) - level
                
                
                # filter dataframes that does not has same parent name
                #print ('NAME_' + parts_parent_str, '==',parts[partslevel_parent] )
                df = df[ df['NAME_' + parts_parent_str ] == parts[partslevel_parent ]]
                
            #df = df.dissolve(by='NAME_'+str(level))
            (y,x) = centroid(df)
            #y = float(df.centroid.y)
            #x = float(df.centroid.x)
            
        DFCACHE[fullname] = (y,x)
        if return_uid:

            DFCACHE_UID[fullname] = int(df.UID)
            return DFCACHE_UID[fullname]
        else:
            return DFCACHE[fullname]
        # find the centroid.
            
    except:
        # LOCALNAME
        
        try:
            place = LOCALNAMES[parts[0]]
            DFCACHE[fullname] = place[1]    
            if return_uid:
                return None
            else:
                return DFCACHE[fullname]
        
        except:
                
            print("geocode error:", fullname)
            return None
    
    
    

#USA = [L0,L1,L2]
    

