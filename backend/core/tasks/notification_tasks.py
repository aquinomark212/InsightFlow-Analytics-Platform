from channels.layers import get_channel_layer

def send_dashboard_update(data):
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
    "dashboard",
    {
        "type": "dashboard_message",
        "data": data
    }
)