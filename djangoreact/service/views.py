from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from django.db.models import Prefetch, Q

from .ds.collaborative_recommender import *
from .ds.ott_recommender import get_ott_recommendations
from .serializers import OTTserviceSerializer
from .models import OTTservice, ContentRecommendation
from entertainment.models import Contents, OTT
from entertainment.serializers import ContentSerializer, OTTSerializer, ContentAndRecommendSerializer
from mypage.models import *

import random

# Create your views here.

# OTTservice APIVIEWS

class OTTserviceCreateView(CreateAPIView):
    name = "OTTservice"
    serializer_class = OTTserviceSerializer
    authentication_classes = [TokenAuthentication]
    permissions_class = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        age = serializer.data.get('age')
        gender = serializer.data.get('gender')
        member_number = serializer.data.get('member_number')
        member_child_count = serializer.data.get('member_child_count')
        member_adult_count = serializer.data.get('member_adult_count')
        pixel = serializer.data.get('pixel')
        price_range = serializer.data.get('price_range')
        genre = serializer.data.get('genre')
        first = serializer.data.get('first')
        second = serializer.data.get('second')
        third = serializer.data.get('third')
        prefer_contents = serializer.data.get('prefer_contents')
        
        # db에 입력 정보 넣어줌.(데이터 분석팀의 요청)
        user_taste = OTTservice.objects.create(
            user = request.user,
            age = age,
            gender = gender,
            member_number = member_number,
            member_child_count = member_child_count,
            member_adult_count = member_adult_count,
            pixel = pixel,
            price_range = price_range,
            genre = genre,
            first = first,
            second = second,
            third = third
        )
        tmdb_id_list = []
        for content in prefer_contents:
            prefer_content = Contents.objects.get(id=content)
            tmdb_id_list.append(str(prefer_content.tmdb_id))
            user_taste.prefer_contents.add(prefer_content)
        user_taste.tmdb_id = ",".join(tmdb_id_list)
        user_taste.save()
        
        tmdb_id_list = [int(x) for x in tmdb_id_list]
        
        recommend_ott = get_ott_recommendations(age, gender, member_number, member_child_count, member_adult_count, pixel, price_range, genre, first, second, third, tmdb_id_list)
                
        # mypage에 들어갈 myott
        for i in range(4):
            MyOTT.objects.create(user=request.user, ott=OTT.objects.get(name__icontains = recommend_ott[i]))
        
        # queryset 만들기
        queryset = OTT.objects.filter(
            Q(name__icontains=recommend_ott[0]) | 
            Q(name__icontains=recommend_ott[1]) | 
            Q(name__icontains=recommend_ott[2]) |
            Q(name__icontains=recommend_ott[3])
        )
        
        OTTserrializer = OTTSerializer(queryset, many=True)
        
        headers = self.get_success_headers(serializer.data)
        return Response(OTTserrializer.data, status=status.HTTP_201_CREATED, headers=headers)


    
    


genre_list = [
    'Drama',
    'Comedy',
    'Action',
    'Adventure',
    'International',
    'Family',
    'Animation',
    'Horror',
    'Romance',
    'Thriller',
    'Fantasy',
    'Drama',
    'Sci'
]

class GiveTopContentByGenre(ListAPIView):
    name = "Give Top Contents By Genre"
    serializer_class = ContentSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        random_int = random.randint(0, 8)
        
        queryset = Contents.objects.filter(
            genre__icontains=genre_list[0]
        ).order_by('-vote_count', '-rating')[random_int:random_int+2]
        
        for genre in genre_list:
            qs = Contents.objects.filter(
                genre__icontains=genre
                ).order_by('-vote_count', '-rating')[random_int:random_int+2]
            queryset = queryset.union(qs)
        
        return queryset


class ContentRecommendServiceListView(ListAPIView):
    name = "MovieRecommend"
    serializer_class = ContentAndRecommendSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = OTT.objects.all()[0:1]
    
    def get_queryset(self):
        current_user = self.request.user.id
        queryset = OTT.objects.all()[0:1]
        
        result = new_collaborative(current_user)

        for i in range(len(result)):
            tmdb_id = (result[i][0])
            score = result[i][2]
            content = Contents.objects.filter(tmdb_id=tmdb_id)[0]
            recommend = ContentRecommendation(user=self.request.user, recommend_content=content, score=score)
            recommend.save()
        
        # tmdb_id 때문에 어쩔 수 없이 역참조 사용..
        
        queryset = Contents.objects.filter(tmdb_id=result[0][0])[0:1]
        
        for i in range(1, len(result)):
            qs = Contents.objects.filter(tmdb_id=result[i][0])[0:1]
            queryset = queryset | qs
        
               
        queryset = queryset.prefetch_related(
            Prefetch('contentrecommendation_set', 
                     queryset = ContentRecommendation.objects.filter(user_id=current_user).order_by('-created_at'))
            ).order_by('?')
    
        return queryset
    
        
