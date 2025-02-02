from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from buy.models import buy, buyer, consumer
from Group.models import Group, Members
from rest_framework import permissions
from rest_framework.generics import CreateAPIView
from buy.serializers import BuySerializer, CreateBuySerializer, BuyListSerializer
from Group.permissions import IsGroupUser
import logging
import dependencies

logger = logging.getLogger('django')

class CreateBuyView(CreateAPIView):
    serializer_class = CreateBuySerializer
    permission_classes = [permissions.IsAuthenticated and IsGroupUser]

    def perform_create(self, serializer):
        logger.info("Perfoming create")
        return serializer.save(added_by=self.request.user)

    def create(self, request, *args, **kwargs):
        logger.info("Request received: POST buy/CreateBuy")
        logger.info("User is authenticated.")
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        logger.info("Serializer data is valid.")

        instance = self.perform_create(serializer)
        instance_serializer = BuyListSerializer(instance)

        logger.info("Created buy instance data. {}".format(instance_serializer.data))
        return Response(instance_serializer.data)


class GetGroupBuys(APIView):
    permission_classes = [permissions.IsAuthenticated and IsGroupUser]

    def post(self, request):
        try:
            perch = dependencies.filter_servise_instance.FilterByGroup(request.data['groupID'], "buy")
            #perch = buy.objects.filter(groupID=request.data['groupID'])

            if 'sort' in request.data:
                perch = perch.order_by('cost')
            perchase = BuySerializer(perch, many=True)
            logger.info('Group buys retrieved successfully. Group ID: {}. Number of buys: {}'.format(request.data['groupID'], len(perchase.data)))
            return Response(perchase.data)
        
        except Exception as e:
            logger.error('An error occurred while retrieving group buys. Group ID: {}'.format(request.data['groupID']))
            logger.error('Error: {}'.format(str(e)))
            return Response({'message': 'An error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserGroupBuys(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        
        try:
            user_id = request.user.user_id
            group_id = request.data.get('groupID')
            
            group_exists = dependencies.filter_servise_instance.FilterByGroup(group_id,"Group").exists()
            # group_exists = Group.objects.filter(id=group_id).exists()
            if not group_exists:
                logger.warning('Group ID not provided. GroupID:{}'.format(group_id))
                return Response({'error': 'Group ID not provided'}, status=status.HTTP_400_BAD_REQUEST)
            
            members_exists = dependencies.filter_servise_instance.FilterByBoth(user_id, group_id, "Members").exists()
            #Members.objects.filter(groupID=group_id, userID=user_id).exists()
            if not members_exists:
                logger.warning('User is not a member of the group. Group ID: {}, User ID: {}'.format(group_id, user_id))
                return Response({'error': 'User is not a member of the group.'}, status=status.HTTP_403_FORBIDDEN)

            # buyer_buys = buy.objects.filter(Buyers__userID=user_id, groupID=group_id).distinct()
            buyer_buys=dependencies.filter_servise_instance.FilterByBoth(user_id, group_id, "buy_Buyer")

            #consumer_buys = buy.objects.filter(consumers__userID=user_id, groupID=group_id).distinct()
            consumer_buys=dependencies.filter_servise_instance.FilterByBoth(user_id, group_id, "buy_consumer")
            
            if 'sort' in request.data:
                consumer_buys = consumer_buys.order_by('cost')
                buyer_buys = buyer_buys.order_by('cost')
            
            logger.debug('Buyer buys count: {}'.format(buyer_buys.count()))
            logger.debug('Consumer buys count: {}'.format(consumer_buys.count()))
            
            consumer_serializer = BuySerializer(consumer_buys, many=True)
            buyer_serializer = BuySerializer(buyer_buys, many=True)

            response_data = {
                    'buyer_buys': buyer_serializer.data,
                    'consumer_buys': consumer_serializer.data
                }
            logger.info('Group buys retrieved successfully for Group ID: {}, User ID: {}'.format(group_id, user_id))
            return Response(response_data, status=status.HTTP_200_OK)
        
        except:
            logger.error('An error occurred while retrieving group buys. Group ID: {}, User ID: {}'.format(group_id, user_id))
            return Response({'message': 'An error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
