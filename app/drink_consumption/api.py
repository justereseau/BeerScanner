# from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required

import csv
from django.http import HttpResponse

from .models import *
from .serializers import *


class ContainerViewSet(viewsets.ModelViewSet):
    queryset = Container.objects.all()
    serializer_class = ContainerSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ContainerViewSet(viewsets.ModelViewSet):
    queryset = Container.objects.all()
    serializer_class = ContainerSerializer


@api_view(['POST'])
def tag_scan(request):
    create_reader = False
    create_tag = False
    try:
        reader = Reader.objects.get(physical_id=request.data['reader_id'])
    except Reader.DoesNotExist:
        reader = Reader.objects.create(physical_id=request.data['reader_id'])
        reader.save()
        create_reader = True

    try:
        tag = Tag.objects.get(uid=request.data['tag_id'])
    except Tag.DoesNotExist:
        tag = Tag.objects.create(uid=request.data['tag_id'])
        tag.save()
        create_tag = True

    if create_reader or create_tag:
        result = {}
        result['result'] = 'success'
        if create_reader:
            result['reader'] = ReaderSerializer(reader).data
        if create_tag:
            result['tag'] = TagSerializer(tag).data
        return Response(result, status=status.HTTP_201_CREATED)

    product = reader.forTap.onTap
    user = tag.owner
    container = tag.linked_container

    Refill.objects.create(user=user, tag=tag, product=product, container=container).save()

    result = {}
    result['result'] = 'success'
    result['container'] = container.name
    result['user'] = UserSerializer(user).data
    result['product'] = ProductSerializer(product.product).data
    result['cost'] = round(product.cost/product.capacity*container.capacity, 2)

    return Response(result)

@staff_member_required
def get_reffil_list(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="history.csv"'},
    )

    writer = csv.writer(response)
    writer.writerow(["id","created_at","user","product","container","cost"])

    refills = Refill.objects.all()
    for refill in refills:
        writer.writerow([refill.id, refill.created_at, refill.user.username, refill.product.product, refill.container, refill.cost()])

    return response
