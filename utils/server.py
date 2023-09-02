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
    print(stdout)
    print("_______________________")
    if has_resp:
        return stdout[0].decode("utf-8")


async def install(ip_address, password):
    cmd = f"/root/script/mpivpn {ip_address} {password} install"
    resp = await execute_command(cmd, has_resp=True)
    print(resp)
    pattern = re.compile('API Outline: "apiUrl":"(.*)","certSha256":"(.*)"}')
    match = re.search(pattern, resp)
    if match is None:
        return {"status": False, "resp": resp}
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


async def delete_wireguard_config(ip_address, password, device_id):
    cmd = f'/root/script/mpivpn {ip_address} {password} "pivpn remove -y u{device_id}"'
    await execute_command(cmd, has_resp=True)


async def disable_wireguard_config(ip_address, password, device_id):
    cmd = f'/root/script/mpivpn {ip_address} {password} "pivpn off -y u{device_id}"'
    await execute_command(cmd, has_resp=True)


async def enable_wireguard_config(ip_address, password, device_id):
    cmd = f'/root/script/mpivpn {ip_address} {password} "pivpn on -y u{device_id}"'
    await execute_command(cmd, has_resp=True)


class Outline:
    def __init__(self, outline_url, outline_sha):
        self.manager = Manager(apiurl=outline_url, apicrt=outline_sha)

    def create_client(self, user_id, limit):
        client = self.manager.new()
        self.manager.rename(client["id"], str(user_id))
        self.set_data_limit(client["id"], limit)
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
        data = {"limit": {"bytes": limit * (1000 ** 3)}}
        requests.put(f"{self.manager.apiurl}/access-keys/{client_id}/data-limit", json=data, verify=False)

    def delete_client(self, client_id):
        self.manager.delete(client_id)

    def get_usage_data(self, client_id):
        return self.manager.usage(client_id)

#
# outline = Outline("https://159.100.9.87:10138/x2_Sz0x9SPqfId0WW2UIvA",
#                   "DD9F4F1148AF61BFAB394E88CA3A619D1822DECA181583C6EBDCB7DCF57C4CE2")
# print(outline.set_data_limit(11, 1))
