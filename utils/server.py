import asyncio
import re

import qrcode as qrcode


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
    print(cmd)
    resp = await execute_command(cmd, has_resp=True)
    print(resp)
    pattern = re.compile('API Outline: "apiUrl":"(.*)","certSha256":"(.*)"}')
    match = re.search(pattern, resp)
    if match is None:
        return {"status": False}
    print(match.group(1))
    print(match.group(2))
    return {"status": True, "outline_url": match.group(1), "outline_sha": match.group(2)}


async def create_wireguard_config(ip_address, password, user_id):
    cmd = f'/root/script/mpivpn {ip_address} {password} "pivpn add -n u{user_id}"'
    resp = await execute_command(cmd, has_resp=True)
    print(resp)
    await get_wireguard_config(ip_address, password, user_id)


async def get_wireguard_config(ip_address, password, user_id):
    cmd = f'/root/script/mpivpn {ip_address} {password} "cat /home/wgvpn/configs/u{user_id}.conf" > u{user_id}.conf'
    await execute_command(cmd, has_resp=True)
    with open(f"u{user_id}.conf") as fh:
        img = qrcode.make(fh.read())
        img.save(f"u{user_id}.png")
