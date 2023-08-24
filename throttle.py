import os
import requests
from transmission_rpc import Client, TransmissionError
import yaml
import logging

logging.basicConfig(level=logging.DEBUG) 

with open(f"{os.path.dirname(os.path.realpath(__file__))}/config.yaml", 'r') as stream:
    config = yaml.safe_load(stream)

def get_plex_streams_count():
    params = {"apikey": config['tautulli']['apikey'], "cmd": "get_activity"}
    response = requests.get(f"{config['tautulli']['baseurl']}/api/v2", params=params)
    data = response.json()
    
    stream_count = len(data["response"]["data"]["sessions"])
    return stream_count

# Options https://transmission-rpc.readthedocs.io/en/v4.3.0/_modules/transmission_rpc/client.html
def transmission_set_limit(download_limit: int, upload_limit: int):
    try:
        with Client(
            host=config['transmission']['host'],
            port=config['transmission']['port'],
            username=config['transmission']['username'],
            password=config['transmission']['password']
        ) as client:
            client.set_session(
                speed_limit_up=upload_limit, 
                speed_limit_up_enabled=True,
                speed_limit_down=download_limit,
                speed_limit_down_enabled=True
            )
            
        logging.info(f"Transmission download speed limit set to {download_limit} kB/s")
        logging.info(f"Transmission upload speed limit set to {upload_limit} kB/s")
    except TransmissionError as e:
        logging.exception(f"Failed to set Transmission upload speed limit: {e}")

def throttle_webhook(message: str):
    logging.debug(f"Sending webhook: {message}")
    for webhook_url in config['webhooks']:
        requests.post(webhook_url, json={'content': message})

def check():
    streams_count = get_plex_streams_count()
    logging.debug(streams_count)
    
    if streams_count >= config['throttling']['stream_count']:
        transmission_set_limit(config['speed']['throttled']['download'], config['speed']['throttled']['upload'])
        throttle_webhook(f"Throttling enabled. {streams_count} streams detected.")
    else:
        transmission_set_limit(config['speed']['normal']['download'], config['speed']['normal']['upload'])

if __name__ == "__main__":
    check()
    # while True:
    #     time.sleep(10) 
