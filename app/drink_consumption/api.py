from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

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


@api_view(['POST'])
def tag_scan(request):
    create_reader = False
    create_tag = False
    
    channel_layer = get_channel_layer()
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

        result['type'] = 'register_reader_or_tag'
        async_to_sync(channel_layer.group_send)('refill_notification', result)

        return Response(result, status=status.HTTP_201_CREATED)

    result = {}
    result['type'] = 'register_reffil'
    result['errors'] = []

    if reader.forTap is None:
        result['errors'].append({
            'name': "reader_not_configured",
            'error_message': "Reader " + str(reader.physical_id) + " (id: " + str(reader.id) + ") is not configured."
        })
    elif reader.forTap.onTap is None:
        result['errors'].append({
            'name': "tap_not_configured",
            'error_message': "Tap \"" + str(reader.forTap) + "\" (id: " + str(reader.forTap.id) + ") is not configured."
        })

    if tag.owner is None:
        result['errors'].append({
            'name': "tag_not_configured",
            'error_message': "Tag \"" + str(tag) + "\" (id: " + str(tag.id) + ") is not configured."
        })

    if len(result['errors']) > 0:
        result['result'] = 'error'
        async_to_sync(channel_layer.group_send)('refill_notification', result)
        return Response(result, status=status.HTTP_412_PRECONDITION_FAILED)

    product = reader.forTap.onTap
    user = tag.owner
    container = tag.linked_container

    if product.refill_capacity_override is not None:
        capacity = product.refill_capacity_override
        container_name = "can"
    else:
        capacity = container.capacity
        container_name = container.name

    Refill.objects.create(user=user, tag=tag, product=product, capacity=capacity).save()
    
    result = {}

    refills = Refill.objects.filter(user=user)
    volume = 0
    drinks = 0
    cost = 0
    for refill in refills:
        drinks += 1
        volume += refill.capacity
        cost += refill.cost()

    result = {}
    result['result'] = 'success'
    result['container'] = container_name
    result['user'] = UserSerializer(user).data
    result['product'] = ProductSerializer(product.product).data
    result['cost'] = round(product.cost/product.capacity*capacity, 2)

    result['user']['drinks'] = drinks
    result['user']['cost'] = round(cost, 2)

    result['type'] = 'register_reffil'
    async_to_sync(channel_layer.group_send)('refill_notification', result)

    return Response(result, status=status.HTTP_202_ACCEPTED)

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

@api_view(['GET'])
def players(request):
    players = User.objects.filter(groups__name='players', is_active=True)

    if 'tag_id' in request.GET:
        tag = get_object_or_404(Tag, uid=request.GET['tag_id'])
        player = tag.owner
        return Response(UserSerializer(player).data, status=status.HTTP_200_OK)

    players_d = []

    for player in players:
        refills = Refill.objects.filter(user=player)
        volume = 0
        drinks = 0
        for refill in refills:
            drinks += 1
            volume += refill.capacity

        if player.first_name == "":
            name = player.username
        else:
            name = player.first_name

        if volume < 1:
            volume_s = str(round(volume * 1000, 2)) + "mL"
        else:
            volume_s = str(round(volume, 2)) + "L"

        players_d.append({'name': name, 'username': player.username, 'reffils': drinks, 'volume': volume_s, 'liters': volume })

    players_d.sort(key=lambda x: x.get('liters'), reverse=True)
    result = {'results': players_d}
    return Response(result)

@api_view(['GET'])
def taps(request):
    taps = Tap.objects.all()
    taps_d = []
    for tap in taps:
        if tap.onTap is not None:
            taps_d.append({'onTap': ProductSerializer(tap.onTap.product, context={'request': request}).data, 'remaining': round(tap.onTap.remaining(), 2)})

    result = {'results': taps_d}
    return Response(result)

@api_view(['GET'])
def last_scan(request):
    players = User.objects.filter(groups__name='players', is_active=True)

    players_d = []

    for player in players:
        refills = Refill.objects.filter(user=player)
        volume = 0
        drinks = 0
        for refill in refills:
            drinks += 1
            volume += refill.container.capacity

        if player.first_name == "":
            name = player.username
        else:
            name = player.first_name

        if volume < 1:
            volume_s = str(round(volume * 1000, 2)) + "mL"
        else:
            volume_s = str(round(volume, 2)) + "L"

        players_d.append({'name': name, 'username': player.username, 'reffils': drinks, 'volume': volume_s, 'liters': volume})

    players_d.sort(key=lambda x: x.get('liters'), reverse=True)
    result = {'results': players_d}
    return Response(result)

@api_view(['GET'])
def cans(request):
    containers = Container.objects.filter(refill_capacity_override__isnull=False)
    containers_d = []
    for container in containers:
        can_cost = container.cost/container.capacity*container.refill_capacity_override
        containers_d.append({'name': container.product.name, 'remaining': round(container.remaining()/container.refill_capacity_override), 'cost': round(can_cost, 2), 'batch_number': container.product.batch_number})
    result = {'results': containers_d}
    return Response(result)

@api_view(['POST'])
def buy_a_can(request, batch):
    if 'username' not in request.data and 'tag_uuid' not in request.data:
        return Response({'result': 'error', 'reason': 'missing parameters'}, status=status.HTTP_400_BAD_REQUEST)

    if 'tag_uuid' in request.data:
        tag = get_object_or_404(Tag, uid=request.data['tag_uuid'])
        if 'username' not in request.data:
            user = tag.owner
        else:
            user = get_object_or_404(User, username=request.data['username'])
    else:
        tag = None
        user = get_object_or_404(User, username=request.data['username'])

    product = get_object_or_404(Product, batch_number=batch)
    container = get_object_or_404(Container, product=product)

    if container.remaining() < container.refill_capacity_override:
        return Response({'result': 'error', 'reason': 'no more can'}, status=status.HTTP_400_BAD_REQUEST)

    refill = Refill(user=user, product=container, capacity=container.refill_capacity_override)

    if tag is not None:
        refill.tag = tag

    refill.save()

    result = {
        'param': batch,
        'request': request.data,
        'user': user.username,
        'product': product.name
    }
    return Response(result)
