# python code, project.py
from flask import Flask,render_template,request
import requests
from datetime import datetime

def get_name():
    name = request.args.get('name')
    return name

def check_validity_of_name(name):
    if name == "":
        return render_template('index.html')

def get_rank_tier_LP(encrypted_id):
    url = 'https://kr.api.riotgames.com/tft/league/v1/entries/by-summoner/' + encrypted_id
    response = requests.get(url, headers={"X-Riot-Token": api})

    if response.json():
        tier = response.json()[0]["tier"]
        rank = response.json()[0]["rank"]
        LP = response.json()[0]["leaguePoints"]
        rank_dict = {
        "tier" : tier,
        "rank" : rank,
        "LP" : LP
        }
    else :
        rank_dict = {
        "tier" : "언랭 / 배치중",
        "rank" : "언랭 / 배치중",
        "LP" : "해당사항 없음"
        }
    return rank_dict

def get_my_puuid(encrypted_id):
    url = 'https://kr.api.riotgames.com/tft/summoner/v1/summoners/' + encrypted_id
    response = requests.get(url, headers={"X-Riot-Token": api})
    puuid = response.json()["puuid"]
    return puuid

def get_my_match_id(puuid):
    url = 'https://asia.api.riotgames.com/tft/match/v1/matches/by-puuid/'+ puuid + '/ids?start=0&count=20'
    response = requests.get(url, headers={"X-Riot-Token": api})
    matchID = response.json()[0]
    return matchID

def get_other_summoners(matchID):
    other_summoner_name_list = []
    url = 'https://asia.api.riotgames.com/tft/match/v1/matches/' + matchID 
    response = requests.get(url, headers={"X-Riot-Token": api})
    other_summoner_puuid = response.json()["metadata"]["participants"]
    for x in range (len(other_summoner_puuid)):
        url = 'https://kr.api.riotgames.com/tft/summoner/v1/summoners/by-puuid/' + other_summoner_puuid[x]
        response = requests.get(url, headers={"X-Riot-Token": api})
        other_summoner_name = response.json()["name"]
        other_summoner_name_list.append(other_summoner_name)
    return other_summoner_name_list

# 게임 타입이 랭크 게임이었는지 일반 게임이었는지 확인하는 용도
def get_game_type(matchID):
    url = 'https://asia.api.riotgames.com/tft/match/v1/matches/' + matchID 
    response = requests.get(url, headers={"X-Riot-Token": api})
    queue_id = response.json()["info"]["queue_id"]
    if (queue_id == 1090):
        game_type = '일반'
    elif (queue_id == 1100):
        game_type = '랭크'    
    return game_type

def get_placement(matchID,my_puuid):
    url = 'https://asia.api.riotgames.com/tft/match/v1/matches/' + matchID 
    response = requests.get(url, headers={"X-Riot-Token": api})
    all_summoners = response.json()["info"]["participants"]
    for i in range (len(all_summoners)):
        if (all_summoners[i]["puuid"] == my_puuid):
            placement = all_summoners[i]["placement"]
            return placement

def get_time_length(matchID):
    url = 'https://asia.api.riotgames.com/tft/match/v1/matches/' + matchID
    response = requests.get(url, headers={"X-Riot-Token": api})
    # unixtime_in_ms = response.json()["info"]["game_datetime"]
    length_in_sec = response.json()["info"]["game_length"]
    length = round(length_in_sec / 60)
    return length


def get_time(matchID):
    url = 'https://asia.api.riotgames.com/tft/match/v1/matches/' + matchID 
    response = requests.get(url, headers={"X-Riot-Token": api})
    timestamp = response.json()["info"]["game_datetime"]

    ts = int(timestamp)
    ts /= 1000
    
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    time = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    return time

    # 24시간 이내이면 몇시간 전 게임인지 나타낼 것
    # 24시간 이후 48시간 이전이면 1일 전
    # 그 이후로는 그냥 지금 타임 (현재 get_time 에서 리턴되는 time 으로)

def get_augments_and_traits(matchID,my_puuid):
    url = 'https://asia.api.riotgames.com/tft/match/v1/matches/' + matchID
    response = requests.get(url, headers={"X-Riot-Token": api})
    all_participants = response.json()["metadata"]["participants"]
    augments=response.json()["info"]["participants"][all_participants.index(my_puuid)]["augments"]
    get_number_of_traits=len(response.json()["info"]["participants"][all_participants.index(my_puuid)]["traits"])
    traits_with_tier={}
    for x in range(get_number_of_traits):
        if response.json()["info"]["participants"][all_participants.index(my_puuid)]["traits"][x]['tier_current'] > 0:
            print(x)
            traits_with_tier.update({response.json()["info"]["participants"][all_participants.index(my_puuid)]["traits"][x]['name']:response.json()["info"]["participants"][all_participants.index(my_puuid)]["traits"][x]['tier_current']})
    
    for i in range(0, 3):
        if augments[i] == 'TFT7_Augment_CavalierTrait':
            augments[i] = '기병대 심장'
        elif augments[i] == 'TFT7_Augment_AxiomArc1':
            augments[i] = '원칙의 원형낫 I'
        elif augments[i] == 'TFT6_Augment_SecondWind2':
            augments[i] = '재생의 바람 II'


    augments_and_traits = {
        "augments" : augments,
        "traits_with_tier" : traits_with_tier
    }
    print("augments and traits with dict form", augments_and_traits)

    return augments_and_traits


#-----------------------------------------------------------------------------------#
app = Flask(__name__, template_folder="templates")
api = 'RGAPI-6cf8c713-86be-4205-8be5-44b697a1cfd8'

@app.route('/')
def index():
    return render_template('index.html')
    
@app.route('/get_info')
def get_info():
    # 소환사 명
    name = get_name()
    print(name)
 
    # No entry
    if not name:
        return render_template('index.html')
    else:
        #get response by name
        url = 'https://kr.api.riotgames.com/tft/summoner/v1/summoners/by-name/' + name
        response = requests.get(url, headers={"X-Riot-Token": api})
        # print(response)

        if response.status_code == 404:
            length, result = 0, 0
            return render_template('result.html', length = length, result = result)
        else:
            encrypted_id = response.json()["id"]
            print("encrypted summoner id:", encrypted_id)
            if not encrypted_id:
                return render_template('index.html')
            else:

                # 랭크 & 티어
                ranks_tier_LP = get_rank_tier_LP(encrypted_id)
                print('rank is:', ranks_tier_LP)

                #get my puuid
                my_puuid = get_my_puuid(encrypted_id)
                print("my puuid: ", my_puuid)

                #get match id
                my_match_id = get_my_match_id(my_puuid)
                print("my match id:", my_match_id)
                
                #find other summoners using matchID
                other_summoner_in_game = get_other_summoners(my_match_id)
                print("other_summoner_in_game:", other_summoner_in_game)

                #get game type
                game_type = get_game_type(my_match_id)
                print("game type was: ", game_type)

                placement = get_placement(my_match_id,my_puuid)
                print("placement: ", placement)

                game_time = get_time(my_match_id)
                print("time:", game_time)

                time_length = get_time_length(my_match_id)
                print("time and length:", time_length)

                augments_and_traits=get_augments_and_traits(my_match_id, my_puuid)
                print("my augments and traits were:", augments_and_traits)

                result = {
                    "ranks_tier_LP" : ranks_tier_LP,
                    "time" : game_time,
                    "game_type" : game_type,
                    "placement" : placement,
                    "time_length" : time_length,
                    "augments_and_traits" : augments_and_traits
                }
                
                return render_template('result.html', name = name, result=result, other_summoner_in_game=other_summoner_in_game)

# 메인 테스트
if __name__ == "__main__":
    app.run(debug=True)