from labbot.commands import commands

@commands.command()
async def echo(event, gl, message):
    url = f"/projects/{event.project_id}/issues/{event.data['issue']['iid']}/notes"
    await gl.post(url, data={"body": message})

@commands.command()
async def time(event, gl):
    url = f"/projects/{event.project_id}/issues/{event.data['issue']['iid']}/notes"
    await gl.post(url, data={"body": event.data["issue"]["updated_at"]})

def setup(bot) -> None:
    pass
