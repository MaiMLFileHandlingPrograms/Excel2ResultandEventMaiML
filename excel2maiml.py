import os, sys
import copy,hashlib,mimetypes
import uuid as UUID
import pandas as pd
from pathlib import Path
from Utils.staticClass import maimlelement
from Utils.createMaiMLFile import  ReadWriteMaiML, UpdateMaiML


################################################
## FILE DIR PATH 
################################################
class filepath:
    cur_file = __file__  #このファイルのパス
    codedir = os.path.dirname(cur_file) + '/'
    rootdir = os.path.abspath(os.path.join(codedir, os.pardir)) + '/'
    input_dir = codedir + 'INPUT/'
    output_dir = codedir + 'OUTPUT/'

    
### excelの日付データのフォーマットを変換 ###################################
## YYYY-MM-DDTHH:MM:SS-xx:xx #########
def changeTimeFormat(e_datetime):
    #print(e_datetime) #2024/3/5 9:03
    e_datetime = pd.to_datetime(e_datetime)
    #print(e_datetime) # 2024-03-05 09:03:00
    TIME_ZONE = 'Asia/Tokyo'
    e_datetime = e_datetime.tz_localize(TIME_ZONE)
    # 日時を 'YYYY-MM-DDTHH:MM:SS' フォーマットに変換
    datetime_str = e_datetime.strftime('%Y-%m-%dT%H:%M:%S')
    # タイムゾーンオフセットを取得してフォーマットする
    offset = e_datetime.strftime('%z')
    formatted_offset = offset[:3] + ':' + offset[3:]  # '+09:00'
    # 日付とタイムゾーンオフセットを合体
    datetime = f'{datetime_str}{formatted_offset}'
    #print(datetime) # 2024-03-05T09:03:00-09:00
    return datetime

    
### insertionコンテンツを作成 #################################################
def makeInsertion(value, otherspath):
    filename = str(value)
    file_path = otherspath / filename
    # formatの取得
    extension = os.path.splitext(filename)[1]
    mime_type=''
    hash_sha256 = ''
    mimetypes.init()
    try:
        mime_type = mimetypes.types_map[extension]
    except Exception as e:
        print("insertion file's mime_type is not exist.: ",e)
        mime_type = 'none'
    try:
        with open(file_path, 'rb') as f:
            hash_sha256 = hashlib.sha256()
            while chunk := f.read(8192):  # 8KBごとにファイルを読み込む
                hash_sha256.update(chunk) 
            hash_sha256 = hash_sha256.hexdigest()
    except FileNotFoundError:
        print("insertion file's name '" + filename + "' does not exist.")
    except Exception as e:
        raise e
    insertion_dict = {
        maimlelement.uri:'./'+ filename,
        maimlelement.hash:str(hash_sha256),
        maimlelement.format:mime_type
        } 
    return insertion_dict


### propertyのコンテンツを作成 #################################################
def makeProperty(propertylist,key,value):
    #propertylist = instancedict[maimlelement.property]
    for propertydict in propertylist:
        if propertydict[maimlelement.keyd] == key:
            propertydict[maimlelement.value] = str(value)
            return propertylist
        else:
            pass
        if maimlelement.property in propertydict.keys():
            propertylist2 = propertydict[maimlelement.property] if isinstance(propertydict[maimlelement.property],list) else [propertydict[maimlelement.property]]
            propertylist = makeProperty(propertylist2,key,value) 
    return propertylist


def main(maimlpath, exfilepath, otherspath):
    ## 1. MaiML
    ### 1-1. 読み込む
    readWriteMaiML = ReadWriteMaiML()
    maimldict = readWriteMaiML.readFile(maimlpath)
    
    ### 1-2. maimlのprotocolからdata,eventLogの仮データを作成
    updateMaiML = UpdateMaiML()
    fullmaimldict = updateMaiML.createFullMaimlDict(maimldict) 
    
    ### 1-3. 計測データを書き出すための準備
    #### 1-3-1. results実データ作成の準備
    resultsdict__ = fullmaimldict[maimlelement.maiml][maimlelement.data].pop(maimlelement.results)
    resultslist = []
    
    ### 1-4. methodのIDを取得
    methoddict_ = maimldict[maimlelement.maiml][maimlelement.protocol][maimlelement.method]
    methodIDlist = methoddict_ if isinstance(methoddict_,list) else [methoddict_]
    
    for methoddict in methodIDlist:
        ### 1-5. instructionのIDを取得 programは１つとする
        programdict = methoddict[maimlelement.program]
        instructionID_ = programdict[maimlelement.instruction][maimlelement.idd]
        instructionIDlist = instructionID_ if isinstance(instructionID_,list) else [instructionID_]
        #### 1-3-2. trace実データ作成の準備
        logdict_ = fullmaimldict[maimlelement.maiml][maimlelement.eventlog][maimlelement.log]
        loglist = logdict_ if isinstance(logdict_,list) else [logdict_]
        tracedict__ = {}
        tracelist__ = []
        for logdict in loglist:
            if(logdict[maimlelement.refd] == methoddict[maimlelement.idd]):
                tracelist__ = logdict.pop(maimlelement.trace)
                tracelist__ = tracelist__ if isinstance(tracelist__,list) else [tracelist__]
                for tracedict1 in tracelist__:
                    tracedict__ = tracedict1 if tracedict1[maimlelement.refd] == programdict[maimlelement.idd] else {}
        tracelist = []
                        
        ## 2. エクセルを読み込む
        df = pd.read_excel(exfilepath, sheet_name=methoddict[maimlelement.idd], header=None)
        ### 2-1. 1行目と2行目のデータを取り出しておく(テンプレートのID、キー)
        ### 2-1-1. 1行目のデータ
        row1_1 = df.iloc[0]
        templateIDdict = {}
        '''
            templateIDdict = {
                'templateID1':[列番号のリスト],
                'templateID2':[列番号のリスト],
                }
        '''
        row1 = row1_1[2:]
        for index in row1.index:
            if pd.notna(row1[index]):
                if templateIDdict and row1[index] in templateIDdict.keys(): # 該当キー（templateのID）に値（index）を追加
                    if isinstance(templateIDdict[row1[index]],list):
                        templateIDdict[row1[index]].append(index)
                    else:
                        templateIDdict[row1[index]] = [index]
                else: # キーと値を追加
                    templateIDdict.update({row1[index]:[index]})
        ### 2-1-2. 2行目のデータ
        row2 = df.iloc[1]
        
        ### 2-2. 3行目以降のデータをMaiMLデータに変換
        df_rest = df.iloc[2:]
        ### 2-2-1. 3行目以降のデータ１行ごとにreaults,traceを作成する
        for row3 in df_rest.itertuples(index=True):
            # results
            resultsdict = copy.deepcopy(resultsdict__)
            resultsdict[maimlelement.idd] = resultsdict[maimlelement.idd] + str(row3.Index)
            resultsdict[maimlelement.uuid] = str(UUID.uuid4())
            instancedictlist = []
            instancedictlist.extend(resultsdict[maimlelement.material] if isinstance(resultsdict[maimlelement.material],list) else [resultsdict[maimlelement.material]])
            instancedictlist.extend(resultsdict[maimlelement.condition] if isinstance(resultsdict[maimlelement.condition],list) else [resultsdict[maimlelement.condition]])
            instancedictlist.extend(resultsdict[maimlelement.result] if isinstance(resultsdict[maimlelement.result],list) else [resultsdict[maimlelement.result]])
            
            for id, i_list in templateIDdict.items(): ## エクセルから取得したtemplateIDの数分繰り返し処理
                templateID = id
                instanceID = templateID + '_instance'
                instancedict = next((item for item in instancedictlist if item[maimlelement.idd] == instanceID), None)
                instancedict[maimlelement.uuid] = str(UUID.uuid4())
                instancedict[maimlelement.idd] = instancedict[maimlelement.idd] + str(row3.Index)
                if instancedict: ## エクセルから取得したinstanceIDがmaimlファイルに存在する場合
                    #propertyのvalueを上書き
                    propertylist = instancedict[maimlelement.property] if isinstance(instancedict[maimlelement.property],list) else [instancedict[maimlelement.property]]
                    for id_index in i_list: ## keyの数分popertyにvalueを追加する
                        key = row2[id_index]
                        value = row3[id_index+1]
                        if key == 'INSERTION':
                            if pd.notna(value):
                                insertiondict = makeInsertion(value, otherspath)
                                instancedict[maimlelement.insertion] = insertiondict
                            else:
                                pass
                        else:
                            propertylist = makeProperty(propertylist,key,value)
                else:
                    print(templateID + " does not exist.")     
            resultslist.append(resultsdict)
            
            # trace
            tracedict = copy.deepcopy(tracedict__)
            tracedict[maimlelement.idd] = tracedict[maimlelement.idd] + str(row3.Index)
            tracedict[maimlelement.uuid] = str(UUID.uuid4())
            # instruction（インスタンス）１つに対してeventを１つ
            eventlist = tracedict[maimlelement.event]
            for eventdict in eventlist: # eventlistに含まれるeventdictは１つ
                eventdict[maimlelement.idd] = eventdict[maimlelement.idd] + str(row3.Index)
                eventdict[maimlelement.uuid] = str(UUID.uuid4())
                propertylist = eventdict[maimlelement.property] # 必ずlist
                for propertydict in propertylist:
                    if propertydict[maimlelement.keyd] == maimlelement.time:
                        # 日付のフォーマット変換
                        datetime = changeTimeFormat(row3[2])
                        propertydict[maimlelement.value] = str(datetime)
            tracelist.append(tracedict)
        for logdict in loglist:
            if(logdict[maimlelement.refd] == methoddict[maimlelement.idd]):
                logdict[maimlelement.trace] = tracelist
                    
        fullmaimldict[maimlelement.maiml][maimlelement.data][maimlelement.results] = resultslist
    
    ## outputファイルを保存
    try:
        outmaimlpath = './OUTPUT/output.maiml'
        path, duuid = readWriteMaiML.writecontents(fullmaimldict, outmaimlpath)
    except Exception as e:
        print('Error while writing to the file.',e) 



if __name__ == '__main__':
    maimlfilename = "input.maiml"
    exfilename = 'input.xlsx'
    maimlpath = ''
    exfilepath = ''
    otherspath = ''
    
    if len(sys.argv) > 1:
        rootdir = Path(filepath.input_dir + sys.argv[1])
        if rootdir.exists() and rootdir.is_dir():
            for file in rootdir.rglob('*'):  # rglob('*') で再帰的にすべてのファイルを取得
                if file.is_file():  # ファイルかどうかを確認
                    # ファイル名と拡張子を分けて取得
                    file_extension = file.suffix  # 拡張子を取得
                    if file_extension == '.maiml':
                        maimlfilename = file
                    elif file_extension == '.xlsx':
                        exfilename = file
            maimlpath = rootdir / maimlfilename
            exfilepath = rootdir / exfilename
            otherspath = rootdir
    else:
        maimlpath = Path(filepath.input_dir + 'maiml/'+ maimlfilename)
        exfilepath = Path(filepath.input_dir + 'excel/'+ exfilename)
        otherspath = Path(filepath.input_dir + 'others/')
    try:
        print('INPUT FILES ==')
        print('maimlpath: ',maimlpath)
        print('exfilename: ',exfilepath)
        print('======================')
        main(maimlpath, exfilepath, otherspath)
        print('Successfully created the data file.')
    except Exception as e:
        print('Error : ',e)
     

    