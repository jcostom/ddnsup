#!/usr/bin/env python3

import asyncio
import hmac
import hashlib
import json
import logging
import os
import os.path
import requests
import telegram
from time import strftime, gmtime, sleep

# --- To be passed in to container ---
# Debug is optional, but let's determine if it's on first.
DEBUG = int(os.getenv('DEBUG', 0))

# Required Vars
IPADDR_SRC = os.getenv('IPADDR_SRC', 'https://ipv4.icanhazip.com/')
INTERVAL = int(os.getenv('INTERVAL', 300))
RECORDS = os.getenv('RECORDS')
PROVIDER = os.getenv('PROVIDER')

# Setup logger
LOG_LEVEL = 'DEBUG' if DEBUG else 'INFO'
logging.basicConfig(level=LOG_LEVEL,
                    format='[%(levelname)s] %(asctime)s %(message)s',
                    datefmt='[%d %b %Y %H:%M:%S %Z]')
logger = logging.getLogger()

match PROVIDER:
    case 'cf':
        # Required Vars for Cloudflare
        APITOKEN = os.getenv('APITOKEN')
        CFZONEID = str(os.getenv('CFZONEID'))
        TTL = os.getenv('TTL', 1)
        # Optional Vars for Cloudflare
        PROXIED = str(os.getenv('PROXIED', 'false'))
    case 'dme':
        # Required Vars for DNS Made Easy
        APIKEY = os.getenv('APIKEY')
        SECRETKEY = os.getenv('SECRETKEY')
        DMEZONEID = str(os.getenv('DMEZONEID'))
        TTL = os.getenv('TTL', 1800)
    case 'dnsomatic':
        # Required Vars for DNS-O-Matic
        DOM_USER = os.getenv('DOMUSER')
        DOM_PASSWD = os.getenv('DOMPASSWD')
        DOM_WILDCARD = os.getenv('WILDCARD', 'NOCHG')
        DOM_MX = os.getenv('MX', 'NOCHG')
        DOM_BACKUPMX = os.getenv('BACKUPMX', 'NOCHG')
        # (possibly) redefine RECORDS - If you're using DNS-O-Matic and want to
        # update all services, you don't need to set RECORDS, we'll default to
        # all.dnsomatic.com, which does all your services.
        RECORDS = os.getenv('RECORDS', 'all.dnsomatic.com')
    case _:
        logger.debug(f'Error: PROVIDER variable was set to:[{PROVIDER}]. Exiting.')  # noqa E501
        exit(1)

# Optional Vars
USETELEGRAM = int(os.getenv('USETELEGRAM', 0))
CHATID = int(os.getenv('CHATID', 0))
MYTOKEN = os.getenv('MYTOKEN', 'none')
SITENAME = os.getenv('SITENAME', 'mysite')


# --- Globals ---
VER = '0.8.1'
USER_AGENT = f"ddnsup.py/{VER}"
IPCACHE = "/config/ip.cache.txt"
HTTP_DATE_STRING = '%a, %d %b %Y %H:%M:%S GMT'


def get_current_ip(ip_url: str) -> str:
    return requests.get(ip_url).text.rstrip('\n')


def ip_changed(ip: str) -> bool:
    with open(IPCACHE, "r") as f:
        cached_ip = f.read()
        if cached_ip == ip:
            return False
        else:
            return True


def update_cache(ip: str) -> int:
    with open(IPCACHE, "w+") as f:
        f.write(ip)
    return 0


async def send_notification(msg: str, chat_id: int, token: str) -> None:
    bot = telegram.Bot(token=token)
    await bot.send_message(chat_id=chat_id, text=msg)
    logger.info('Telegram Group Message Sent')


def break_up_records(records: str) -> dict:
    # Breakup passed list of records, strip any spaces
    # Setup dict to be populated to map record
    # Cloudflare's or DME's record_id value.
    # For DNS-O-Matic use, we'll never change the
    # "id" values, as they're irrelevant  # noqa E501
    return dict.fromkeys([record.strip() for record in records.split(',')], 'id')  # noqa E501


def create_hmac(msg: str, key: str) -> str:
    key = bytes(key, 'UTF-8')
    msg = bytes(msg, 'UTF-8')
    digester = hmac.new(key, msg, hashlib.sha1)
    return digester.hexdigest()


def create_cfdns_headers(api_token: str) -> dict:
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    return headers


def create_cfdns_get_req(url: str, api_token: str) -> requests.Response:
    headers = create_cfdns_headers(api_token)
    return requests.get(url, headers=headers)


def get_cfdns_domain_name(zone_id: str, api_token: str) -> str:
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}"
    r = create_cfdns_get_req(url, api_token)
    # Locate and return the zone's name
    return r.json()['result']['name']


def get_cfdns_record_id(zone_id: str, api_token: str, record_name: str,
                        domain_name: str) -> str:
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?name={record_name}.{domain_name}"  # noqa E501
    r = create_cfdns_get_req(url, api_token)
    return r.json()['result'][0]['id']


def update_cfdns_record(zone_id: str, api_token: str,
                        record: list, ip: str) -> requests.Response:
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record[1]}"  # noqa E501
    data = f'{{"type":"A","name":"{record[0]}","content":"{ip}","ttl":{TTL},"proxied":{PROXIED}}}'  # noqa E501
    headers = {"Authorization": f"Bearer {api_token}", "Content-Type": "application/json"}  # noqa E501
    return requests.patch(url, headers=headers, data=data)


def send_cfdns_updates(zone_id: str, api_token: str, records: dict,
                       ip: str, domain: str) -> None:
    for record in records.items():
        update_cfdns_record(zone_id, api_token, record, ip)
        if USETELEGRAM:
            now = strftime("%B %d, %Y at %H:%M")
            notification_text = f"[{SITENAME}] {record[0]}.{domain} changed on {now}. New IP == {ip}."  # noqa E501
            asyncio.run(send_notification(notification_text, CHATID, MYTOKEN))


def create_dme_headers(api_key: str, secret_key: str) -> dict:
    now_str = strftime(HTTP_DATE_STRING, gmtime())
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': USER_AGENT,
        'X-dnsme-apiKey': api_key,
        'X-dnsme-hmac': create_hmac(now_str, secret_key),
        'X-dnsme-requestDate': now_str
    }
    return headers


def create_dme_get_req(url: str, api_key: str,
                       secret_key: str) -> requests.Response:
    headers = create_dme_headers(api_key, secret_key)
    return requests.get(url, headers=headers)


def get_dme_domain_name(zone_id: str, api_key: str, secret_key: str) -> str:
    url = f"https://api.dnsmadeeasy.com/V2.0/dns/managed/{zone_id}"
    r = create_dme_get_req(url, api_key, secret_key)
    # Locate and return the zone's name
    return r.json()['name']


def get_dme_record_id(zone_id: str, api_key: str,
                      secret_key: str, record_name: str) -> str:
    url = f"https://api.dnsmadeeasy.com/V2.0/dns/managed/{zone_id}/records?recordName={record_name}"  # noqa: E501
    r = create_dme_get_req(url, api_key, secret_key)
    # Locate and return the record's record ID
    return str(r.json()['data'][0]['id'])


def update_dme_record(zone_id: str, record: list, ip: str, api_key: str,
                      secret_key: str) -> requests.Response:
    url = f"https://api.dnsmadeeasy.com/V2.0/dns/managed/{zone_id}/records/{record[1]}"  # noqa: E501
    body = {
        "name": record[0],
        "type": "A",
        "value": ip,
        "id": record[1],
        "gtdLocation": "DEFAULT",
        "ttl": TTL
    }
    headers = create_dme_headers(api_key, secret_key)
    return requests.put(url, headers=headers, data=json.dumps(body))


def send_dme_updates(zone_id: str, api_key: str, secret_key: str,
                     records: dict, ip: str, domain: str) -> None:
    for record in records.items():
        update_dme_record(zone_id, record, ip, api_key, secret_key)
        if USETELEGRAM:
            now = strftime("%B %d, %Y at %H:%M")
            notification_text = f"[{SITENAME}] {record[0]}.{domain} changed on {now}. New IP == {ip}."  # noqa E501
            asyncio.run(send_notification(notification_text, CHATID, MYTOKEN))


def send_dnsomatic_updates(user: str, passwd: str, wildcard: str,
                           mx: str, backupmx: str, records, ip: str) -> None:
    headers = {'User-Agent': USER_AGENT}
    for record in records.keys():
        update_url = f"https://updates.dnsomatic.com/nic/update?hostname={record}&myip={ip}&wildcard={wildcard}&mx={mx}&backmx={backupmx}"  # noqa E501
        response = requests.get(update_url, headers=headers,
                                auth=(user, passwd))
        logger.info(f"DNS-O-Matic Response: {response.text}")
        if USETELEGRAM:
            now = strftime("%B %d, %Y at %H:%M")
            notification_text = f"[{SITENAME}] {record} changed on {now}. New IP == {ip}."  # noqa E501
            asyncio.run(send_notification(notification_text, CHATID, MYTOKEN))


def main() -> None:
    my_records = break_up_records(RECORDS)
    match PROVIDER:
        case 'cf':
            my_domain = get_cfdns_domain_name(CFZONEID, APITOKEN)
            for record_name, id in my_records.items():
                my_records[record_name] = get_cfdns_record_id(CFZONEID, APITOKEN, record_name, my_domain)  # noqa E501
        case 'dme':
            my_domain = get_dme_domain_name(DMEZONEID, APIKEY, SECRETKEY)
            for record_name, id in my_records.items():
                my_records[record_name] = get_dme_record_id(DMEZONEID, APIKEY, SECRETKEY, record_name)  # noqa E501
        case 'dnsomatic':
            # nothing needed here - when dnsomatic is used
            # the id fields don't matter
            pass
        case _:
            exit(1)

    while True:
        current_ip = get_current_ip(IPADDR_SRC)

        # check to see if cache file exists and take action
        if os.path.exists(IPCACHE):
            if ip_changed(current_ip):
                update_cache(current_ip)
                logger.info(f"IP changed to {current_ip}")
                # Update DNS & Check Telegram
                match PROVIDER:
                    case 'cf':
                        send_cfdns_updates(CFZONEID, APITOKEN, my_records, current_ip, my_domain)  # noqa E501
                    case 'dme':
                        send_dme_updates(DMEZONEID, APIKEY, SECRETKEY, my_records, current_ip, my_domain)  # noqa E501
                    case 'dnsomatic':
                        send_dnsomatic_updates(DOM_USER, DOM_PASSWD, DOM_WILDCARD, DOM_MX, DOM_BACKUPMX, my_records, current_ip)  # noqa E501
                    case _:
                        exit(1)
            else:
                logger.info('No change in IP, no action taken.')
        else:
            # No cache exists, create file
            update_cache(current_ip)
            logger.info(f"No cached IP, setting to {current_ip}")
            # Update DNS & Check Telegram
            match PROVIDER:
                case 'cf':
                    send_cfdns_updates(CFZONEID, APITOKEN, my_records, current_ip, my_domain)  # noqa E501
                case 'dme':
                    send_dme_updates(DMEZONEID, APIKEY, SECRETKEY, my_records, current_ip, my_domain)  # noqa E501
                case 'dnsomatic':
                    send_dnsomatic_updates(DOM_USER, DOM_PASSWD, DOM_WILDCARD, DOM_MX, DOM_BACKUPMX, my_records, current_ip)  # noqa E501
                case _:
                    exit(1)

        sleep(INTERVAL)


if __name__ == "__main__":
    main()
