from django.contrib.contenttypes.models import ContentType

from django.shortcuts import render

from blog.models import Blog
from read_statistics.utils import (get_7_days_hot_data,
                                   get_seven_days_read_data,
                                   get_today_hot_data, get_yesterday_hot_data)
from django.core.cache import cache


def home(request):
    blog_content_type = ContentType.objects.get_for_model(Blog)
    dates, read_nums = get_seven_days_read_data(blog_content_type)

    # 获取7天热门博客缓存数据
    hot_7_days_data_cache = cache.get('hot_7_days_data_cache')
    if hot_7_days_data_cache is None:
        hot_7_days_data = get_7_days_hot_data(Blog)
        cache.set('hot_7_days_data_cache', hot_7_days_data, 3600)

    context = {}
    context['read_nums'] = read_nums
    context['dates'] = dates
    context['today_hot_data'] = get_today_hot_data(blog_content_type)
    context['yesterday_hot_data'] = get_yesterday_hot_data(blog_content_type)
    context['hot_7_days_data'] = hot_7_days_data_cache
    return render(request, 'home.html', context)
