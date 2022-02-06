import numpy as np
import pandas as pd
from entertainment.models import OTT, Contents


def get_initialized():
    """점수 초기화"""
    weight = {
        "price_range": 0,
        "member_number": 0,
        "genre": 0,
        "member_child_count": 0,
        "pixel": 0,
    }

    ott_score = pd.DataFrame(
        {
            "name": [
                "Netflix Basic",
                "Netflix Standard",
                "Netflix Premium",
                "Disney+ Monthly",
                "Disney+ Yearly",
                "Amazon Monthly",
                "Hulu Advertising",
                "Hulu No Advertising",
                "Hulu + LIVE TV",
            ],
            "score": [0] * 9,
        }
    )
    return weight, ott_score


def get_ott_genre():
    """각 OTT의 가장 많은 15개 장르 가져오기."""
    amazon_genre_top = [
        "Drama",
        "Comedy",
        "Action",
        "Suspense",
        "Kid",
        "Documentary",
        "SpecialInterest",
        "Horror",
        "Romance",
        "Animation",
        "Arts",
        "Entertainment",
        "Culture",
        "ScienceFiction",
        "International",
    ]

    disney_genre_top = [
        "Family",
        "Animation",
        "Comedy",
        "Action",
        "Adventure",
        "Nature",
        "ComingofAge",
        "Fantasy",
        "Documentary",
        "Kid",
        "Drama",
        "Docuseries",
        "ScienceFiction",
        "Historical",
        "Musical",
    ]
    hulu_genre_top = [
        "Drama",
        "Comedy",
        "Adventure",
        "Action",
        "Documentary",
        "Animation",
        "Horror",
        "Reality",
        "Thriller",
        "Crime",
        "International",
        "Family",
        "Romance",
        "Kid",
        "Culture",
    ]

    netflix_genre_top = [
        "International",
        "Drama",
        "Comedy",
        "Action",
        "Adventure",
        "Romance",
        "Documentary",
        "Independent",
        "Family",
        "Thriller",
        "Crime",
        "Kid",
        "Horror",
        "Docuseries",
        "Musical",
    ]
    return amazon_genre_top, disney_genre_top, hulu_genre_top, netflix_genre_top


def nan_to_zero(array):
    """nan값은 0으로 교체"""
    if np.isnan(array).any():
        array = np.where(np.isnan(array), 0, array)
    return array


def min_max_scaler(array):
    """정규화"""
    return (array - min(array)) / (max(array) - min(array))


def get_ott_recommendations(
    age ,
    gender,
    member_number,
    member_child_count,
    member_adult_count,
    pixel,
    price_range,
    genre,
    first,
    second,
    third,
    prefer_contents,
    n=4
):
    """
    유저의 취향에 맞는 OTT 추천하기
    Args:
      age(int) : 유저 나이
      gender(str) : 유저 성별
      member_number(int) : 유저가 공유하고 싶은 사람 수
      member_child_count(int) : 유저가 같이 사용할 아이 수
      member_adult_count(int) : 유저가 같이 사용할 성인 수
      pixel(int) : 유저가 원하는 해상도
      price_range(int) : 유저가 원하는 가격
      genre(str) : 유저의 장르 취향
      first(str) : 유저의 1번째 우선순위
      second(str) : 유저의 2번째 우선순위
      third(str) : 유저의 3번째 우선순위
      prefer_contents(int) : 컨텐츠의 TMDB ID 
      n(int) : 추천할 갯수 (기본 4개)
    Returns:
      list(str) : 유저에게 맞는 OTT n개
    """
    users = pd.DataFrame(
        {
            "gender": [gender],
            "age": [age],
            "member_number": [member_number],
            "member_adult_count": [member_adult_count],
            "member_child_count": [member_child_count],
            "pixel": [pixel],
            "price_range": [price_range],
            "genre": [genre],
            "first": [first],
            "second": [second],
            "third": [third],
            "prefer_contents": [prefer_contents],
        }
    )
    
    
    ott=  pd.DataFrame(list(OTT.objects.all().values()))


    contents = pd.DataFrame(list(Contents.objects.all().values()))

    amazon_genre_top, disney_genre_top, \
    hulu_genre_top,  netflix_genre_top = get_ott_genre()

    user_genre_list = set(genre.split(","))
    amazon_genre = set(amazon_genre_top) & user_genre_list
    disney_genre = set(disney_genre_top) & user_genre_list
    hulu_genre = set(hulu_genre_top) & user_genre_list
    netflix_genre = set(netflix_genre_top) & user_genre_list
    intersection_genre_cnt = list(
        map(len, [amazon_genre, disney_genre, hulu_genre, netflix_genre])
    )
    intersection_genre_cnt = pd.DataFrame(intersection_genre_cnt)

    amazon = set(contents[contents.ott == "amazon"][["content_id"]].values.flatten())
    disney = set(contents[contents.ott == "disney"][["content_id"]].values.flatten())
    hulu = set(contents[contents.ott == "hulu"][["content_id"]].values.flatten())
    netflix = set(contents[contents.ott == "netflix"][["content_id"]].values.flatten())
    user_preffered = set(sum(users["prefer_contents"], []))
    # a,d,h,n
    intersection = [
        amazon & user_preffered,
        disney & user_preffered,
        hulu & user_preffered,
        netflix & user_preffered,
    ]
    intersection_cnt = pd.DataFrame(list(map(len, intersection)))

    weight, ott_score = get_initialized()
    for i in ["price_range", "member_number", "genre", "member_child_count", "pixel"]:
        if users["first"].values == i:
            weight[i] += 0.3
        elif users["second"].values == i:
            weight[i] += 0.5
        elif users["third"].values == i:
            weight[i] += 0.75
        else:
            weight[i] += 0.9

    # normalize
    intersection_normalized = min_max_scaler(intersection_cnt.values)
    intersection_genre_normalized = min_max_scaler(intersection_genre_cnt.values)

    intersection_normalized = 1 - nan_to_zero(intersection_normalized)
    intersection_genre_normalized = 1 - nan_to_zero(intersection_genre_normalized)

    max_users = abs(ott.max_user - users.member_number.values)
    max_users_normalized = min_max_scaler(max_users)

    price = abs(ott.cost - users.price_range.values)
    price_normalized = min_max_scaler(price)

    pixel = abs(ott.pixel - users.pixel.values)
    pixel_normalized = min_max_scaler(pixel)

    # weight adjusted
    if users[["age"]].values < 16 or users[["member_child_count"]].values > 0:
        ott_score.score.iloc[3:5] *= weight["member_child_count"] - 0.2
    
    ott_score.score = (
        max_users_normalized * weight["member_number"]
        + price_normalized * weight["price_range"]
        + pixel_normalized * weight["pixel"]
    )
    # Netflix
    ott_score.score[0:3] = (
        ott_score.score[0:3].values
        + intersection_normalized[3]
        + intersection_genre_normalized[3]
    )  
    # Disney
    ott_score.score[3:5] = (
        ott_score.score[3:5].values
        + intersection_normalized[1]
        + intersection_genre_normalized[1]
    )  
    # Amazon
    ott_score.score[5] = (
        ott_score.score[5]
        + intersection_normalized[0]
        + intersection_genre_normalized[0]
    )  
     # Hulu
    ott_score.score[6:] = (
        ott_score.score[6:].values
        + intersection_normalized[2]
        + intersection_genre_normalized[2]
    ) 

    return [x for x in ott_score.sort_values(by="score")["name"][:n]]
