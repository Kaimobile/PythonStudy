import requests
import json
import bs4
import pandas as pd


def saveFile(filename, content):
    f = open(filename, 'w', encoding = 'utf-8')
    f.write(str(content))
    f.close()

def openFile(filename):
    f = open(filename, 'r', encoding = 'utf-8')
    fget = f.read()
    f.close()
    return fget


def GetListJson():
    url = 'http://mobilecdnbj.kugou.com/api/v3/special/song?'
    content = { 'with_cover': 1,
                'plat': 0,
                'specialid': 516893,
                'page': 1,
                'pagesize': -1,
                'area_code': 1,
                'version': 9051,
                'with_res_tag': 0
                }
    kugouList = requests.get(url, params=content)
    kugouList.encoding = 'unicode'
    kugouListDictRaw = eval(kugouList.text)
    kugouListDict = kugouListDictRaw['data']
    saveFile('List.txt',kugouListDict)

def GetSongInfo(hash_num):
    url = 'http://m.comment.service.kugou.com/index.php?r=commentsv2/getCommentWithLike'
    content = { 'code': 'fc4be23b4e972707f36b8a828a93ba8a',
                'kugouid': '363053020',
                'ver': 3,
                'clienttoken': '1dd816ac1f2d2f72b3a63dacc6bdb3dc1068278d541a46f968df689999b1c683',
                'appid': 1005,
                'clientver': 9051,
                'mid': '286046452573372168580119321849238509024',
                'clienttime': '1539233192',
                'key': 'a9ef9b34c55605d15dc2f10cea1c4fd7',
                'extdata': hash_num,
                'p': 1,
                'pagesize': 20
                }
    songComment = requests.get(url, params=content)
    #songComment.encoding = 'unicode'
    songCommentDictRaw = json.loads(songComment.text)
    songCommentDict = songCommentDictRaw['list']
    saveFile(hash_num[-4:]+'.txt',songCommentDict)
    return songCommentDict

def GetVip(songComment):
    return songComment['vip_type']

def GetId(songComment):
    return songComment['user_id']

def GetText(songComment):
    return len(songComment['content'])

def GetReply(songComment):
    return songComment['reply_num']

def GetLike(songComment):
    temp = str(songComment['like'])
    temp2 = eval(temp)
    return temp2['count']
    
def GetOneSong(songComment):
    songCommentList = list(songComment)
    vip_level = []
    id_num = []
    comment_text = []
    like_num = []
    reply_num = []
    for i in range(19):
        vip_level.append(GetVip(songCommentList[i]))
        id_num.append(GetId(songCommentList[i]))
        comment_text.append(GetText(songCommentList[i]))
        like_num.append(GetLike(songCommentList[i]))
        reply_num.append(GetReply(songCommentList[i]))
    #print(vip_level,id_num,comment_text,like_num,reply_num)
    tempFrame = {   'vip_level': vip_level,
                    'id_num': id_num,
                    'comment_text': comment_text,
                    'like_num': like_num,
                    'reply_num': reply_num
                }
    songFrame = pd.DataFrame(tempFrame)
    return songFrame



def GetListSong():
    #GetListJson()
    tempDict = eval(openFile('List.txt'))
    kugouListNum = tempDict['total']
    kugouListDict = tempDict['info']
    kugouListList = list(kugouListDict)
    finalFrame = pd.DataFrame()
    for i in range(kugouListNum):
        songHash = eval(str(kugouListList[i]))
        finalFrame = pd.concat([finalFrame,GetOneSong(GetSongInfo(songHash['hash']))])
    finalFrame.to_excel('kugoudata.xlsx')
