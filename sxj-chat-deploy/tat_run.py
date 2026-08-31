#!/usr/bin/env python3
# 通用 TAT 单命令执行器：python3 tat_run.py <script_file> [name]
import base64, os, sys, time
from tencentcloud.common import credential
from tencentcloud.tat.v20201028 import tat_client, models

SID = os.environ.get("TENCENT_SECRET_ID", "")
SKEY = os.environ.get("TENCENT_SECRET_KEY", "")
INST = "lhins-oc9amaq1"
REGION = "eu-frankfurt"

cred = credential.Credential(SID, SKEY)
client = tat_client.TatClient(cred, REGION)

def run(script, name="adhoc", timeout_cmd=120):
    content = base64.b64encode(script.encode()).decode()
    assert len(content) <= 65535, "content too long %d" % len(content)
    req = models.RunCommandRequest()
    req.InstanceIds = [INST]
    req.CommandType = "SHELL"
    req.CommandName = name
    req.Content = content
    req.Timeout = timeout_cmd
    resp = client.RunCommand(req)
    inv = resp.InvocationId
    t0 = time.time()
    while time.time() - t0 < 150:
        time.sleep(2)
        q = models.DescribeInvocationsRequest(); q.InvocationIds = [inv]
        r = client.DescribeInvocations(q)
        st = r.InvocationSet[0].InvocationStatus
        if st in ("SUCCESS", "FAILED", "TIMEOUT", "PARTIAL_FAILED"):
            tasks = []
            t = models.DescribeInvocationTasksRequest(); t.Limit = 50
            tr = client.DescribeInvocationTasks(t)
            tasks = [x for x in (tr.InvocationTaskSet or []) if x.CommandName == name]
            outs = []
            for task in tasks:
                trr = task.TaskResult
                o = (getattr(trr, "Output", "") or "") if trr is not None else ""
                ec = getattr(trr, "ExitCode", "?") if trr is not None else "?"
                try:
                    txt = base64.b64decode(o).decode('utf-8', 'replace')
                except Exception:
                    txt = o
                outs.append("%s exit=%s\n%s" % (task.TaskStatus, ec, txt))
            print("=== %s [%s] inv=%s" % (name, st, inv))
            print("\n".join(outs)[:3000])
            return st
    print("WAIT TIMEOUT", inv)
    return "TIMEOUT"

if __name__ == "__main__":
    script = open(sys.argv[1]).read()
    name = sys.argv[2] if len(sys.argv) > 2 else "adhoc"
    sys.exit(0 if run(script, name) == "SUCCESS" else 1)
