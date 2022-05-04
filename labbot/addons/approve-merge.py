"""
automatically merges merge requests if a certain number of approvals
is reached.
"""
import logging

log = logging.getLogger(__name__)

required_approval_count = 2

async def merge_label_hook(event, gl, *args, **kwargs):
    title = event.object_attributes["title"]
    state = event.object_attributes["state"]
    merge_status = event.object_attributes["merge_status"]
    iid = event.object_attributes['iid']

    if state != "opened" or title.lower().startswith("draft"):
        return

    approvals_url = f"/projects/{event.project_id}/merge_requests/{iid}/approvals"
    merge_url = f"/projects/{event.project_id}/merge_requests/{iid}/merge"

    data = await gl.getitem(approvals_url)

    approval_count = len(data["approved_by"])

    if approval_count >= required_approval_count:
        if merge_status == "can_be_merged":
            await gl.put(merge_url)
        else:
            log.debug(f"Cannot merge !{iid} because of its merge_status `{merge_status}`")

def setup(bot):
    bot.register_merge_hook(merge_label_hook)
    pass