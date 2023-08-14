import asyncio
import re


async def execute_command(command, has_resp=False):
    proc = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout = await proc.communicate()
    if has_resp:
        return stdout[0].decode("utf-8")


async def install(ip_address: str, password: str):
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
