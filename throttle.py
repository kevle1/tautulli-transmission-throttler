import requests
import json
import yaml

with open('config.yaml', 'r') as f:
    settings = yaml.safe_load(f)

def update_bandwidth(download: int, upload: int): 
    transmission_auth = (settings['transmission']['username'], settings['transmission']['password'])

    # Get session ID header from first request
    session = requests.post(settings['transmission']['baseurl'], 
        headers={'X-Transmission-Session-Id': ''}, 
        auth=transmission_auth)
    
    transmission_response = requests.post(
        settings['transmission']['baseurl'], 
        headers={
            "X-Transmission-Session-Id": session.headers['X-Transmission-Session-Id'],
            'Content-Type': 'application/json',
        }, 
        data=json.dumps({
            "method": "session-set",
            "arguments": {
                "speed_limit_down_enabled": True,
                "speed_limit_up_enabled": True,
                "speed_limit_down": download,
                "speed_limit_up": upload
            },
        }), 
        auth=transmission_auth)

    print(transmission_response.json())
    if(transmission_response.status_code == 200):
        print("Successfully updated bandwidth settings")

if __name__ == "__main__":
    tautulli_response = requests.get(
        settings['tautulli']['baseurl'], 
        params={
            'apikey': settings['tautulli']['apikey'],
            'cmd': 'get_activity',
            'length': 1
        }).json()

    stream_count = tautulli_response['response']['data']['stream_count']
    speed = settings['speed']
    
    if int(stream_count) > settings['throttling']['stream_count']:
        print("Stream count exceeded throttling threshold, enabling alternate (throttled) speeds on Transmission")
        update_bandwidth(speed['throttled']['download'], speed['throttled']['upload'])
    else:
        print("Stream count below throttling threshold, disabling alternate (throttled) speeds on Transmission")
        update_bandwidth(speed['normal']['download'], speed['normal']['upload'])
