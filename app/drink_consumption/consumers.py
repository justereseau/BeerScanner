import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        async_to_sync(self.channel_layer.group_add)(
            'refill_notification',
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            'refill_notification',
            self.channel_name
        )

    # Receive message for create a new tag or reader
    def register_reader_or_tag(self, event):
        event['message'] = 'new reader or tag'
        self.send(text_data=json.dumps(event))

   # Receive message for new refill register
    def register_reffil(self, event):
        if event['result'] == 'error':
            event['message'] = "errors: "
            for error in event['errors']:
                event['message'] += error['error_message'] + " "
        else:
            event['message'] = 'new reffil'
        self.send(text_data=json.dumps(event))
