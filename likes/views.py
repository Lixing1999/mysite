from django.contrib.contenttypes.models import ContentType
from django.db.models import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import render

from .models import LikeCount, LikeRecord


def error_response(code, message):
    data = {}
    data['status'] = 'ERROR'
    data['code'] = code
    data['message'] = message
    return JsonResponse(data)

def success_response(liked_num):
    data = {}
    data['status'] = 'SUCCESS'
    data['liked_num'] = liked_num
    return JsonResponse(data)

def like_change(request):
    # 获取数据
    user = request.user
    if not user.is_authenticated:
        return error_response(400, 'You are not logged in')

    content_type = request.GET.get('content_type')
    object_id = int(request.GET.get('object_id'))

    try:
        content_type = ContentType.objects.get(model=content_type)
        model_class = content_type.model_class()
        model_obj = model_class.objects.get(pk=object_id)
    except ObjectDoesNotExist:
        return error_response(401, 'Like does not exist')


    # 处理数据
    if request.GET.get('is_like') == 'true':
        # 点赞
        # 获取数据，如果没有就创建
        like_record, created = LikeRecord.objects.get_or_create(content_type=content_type, object_id=object_id, user=user)
        if created:
            # 进行的第一次点赞
            like_count, created = LikeCount.objects.get_or_create(content_type=content_type, object_id=object_id)
            like_count.liked_num += 1
            like_count.save()
            return success_response(like_count.liked_num)
        else:
            # 已经点赞过,不能重复点赞
            return error_response(402, 'You have liked')

    else:
        # 取消点赞
        if LikeRecord.objects.filter(content_type=content_type, object_id=object_id, user=user).exists():
            # 已被点赞，现在取消
            like_record = LikeRecord.objects.get(content_type=content_type, object_id=object_id, user=user)
            like_record.delete()
            # 点赞记录被删除，点赞数-1
            like_count, created = LikeCount.objects.get_or_create(content_type=content_type, object_id=object_id)
            if not created:
                like_count.liked_num -= 1 
                like_count.save()
                return success_response(like_count.liked_num)
            else:
                return error_response(404, 'No data found')
        else:
            # 没有点赞过，不能取消
            return error_response(403, 'You have not liked it')
