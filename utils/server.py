import asyncio
import re

import qrcode as qrcode
import requests
from outline_api import Manager

from config_parser import outline_limit


async def execute_command(command, has_resp=False):
    proc = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout = await proc.communicate()
    if has_resp:
        return stdout[0].decode("utf-8")


async def install(ip_address, password):
    cmd = f"/root/script/mpivpn {ip_address} {password} install"
    resp = await execute_command(cmd, has_resp=True)
    print(resp)
    pattern = re.compile('API Outline: "apiUrl":"(.*)","certSha256":"(.*)"}')
    match = re.search(pattern, resp)
    if match is None:
        return {"status": False}
    print(match.group(1))
    print(match.group(2))
    return {"status": True, "outline_url": match.group(1), "outline_sha": match.group(2)}


async def create_wireguard_config(ip_address, password, device_id):
    cmd = f'/root/script/mpivpn {ip_address} {password} "pivpn add -n u{device_id}"'
    resp = await execute_command(cmd, has_resp=True)
    await get_wireguard_config(ip_address, password, device_id)


async def get_wireguard_config(ip_address, password, device_id):
    cmd = f'/root/script/mpivpn {ip_address} {password} "cat /home/wgvpn/configs/u{device_id}.conf" > u{device_id}.conf'
    await execute_command(cmd, has_resp=True)
    with open(f"u{device_id}.conf") as fh:
        img = qrcode.make(fh.read())
        img.save(f"u{device_id}.png")


class Outline:
    def __init__(self, outline_url, outline_sha):
        self.manager = Manager(apiurl=outline_url, apicrt=outline_sha)

    def create_client(self, user_id):
        client = self.manager.new()
        self.manager.rename(client["id"], user_id)
        self.set_data_limit(client["id"], outline_limit)
        return client

    def get_clients(self):
        clients = self.manager.all()
        return clients

    def get_client(self, client_id):
        clients = self.get_clients()
        for client in clients:
            if client["id"] == client_id:
                return client

    def set_data_limit(self, client_id, limit):
        data = {"limit": {"bytes": limit}}
        requests.put(f"{self.manager.apiurl}/access-keys/{client_id}/data-limit", json=data, verify=False)
