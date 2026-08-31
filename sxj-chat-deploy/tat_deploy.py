#!/usr/bin/env python3
# TAT 分段部署：公示墙内嵌 SXJ 对话框 + chat.html 重定向 + post_wall v1.1
# 目标实例 lhins-oc9amaq1 (eu-frankfurt)；Content=base64(脚本)<=65535，脚本<=49150字符，chunk=48000
import base64, os, sys, time
from tencentcloud.common import credential
from tencentcloud.tat.v20201028 import tat_client, models

SID = os.environ.get("TENCENT_SECRET_ID", "")
SKEY = os.environ.get("TENCENT_SECRET_KEY", "")
INST = "lhins-oc9amaq1"
REGION = "eu-frankfurt"
TAT = "/Coze/Drive/扣子/所有对话/主对话/sxj-chat-deploy/tat_pack"

cred = credential.Credential(SID, SKEY)
client = tat_client.TatClient(cred, REGION)

def b64file(name):
    return open(os.path.join(TAT, name), 'rb').read().decode().replace('\n', '').replace('\r', '').strip()

def run(script, name, timeout_cmd=120):
    content = base64.b64encode(script.encode()).decode()
    assert len(content) <= 65535, f"{name} content too long: {len(content)}"
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
            for fname in ("InstanceId", None):
                try:
                    t = models.DescribeInvocationTasksRequest()
                    if fname:
                        f = models.Filter(); f.Name = fname; f.Values = [INST]
                        t.Filters = [f]
                    t.Limit = 50
                    tr = client.DescribeInvocationTasks(t)
                    tasks = [x for x in (tr.InvocationTaskSet or []) if x.CommandName == name]
                    break
                except Exception as ee:
                    if fname is None:
                        raise
                    print("  filter %s failed: %s" % (fname, ee))
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
            print("\n".join(outs)[:2200])
            if st != "SUCCESS":
                sys.exit("ABORT at %s status=%s inv=%s" % (name, st, inv))
            return
    sys.exit("WAIT TIMEOUT %s inv=%s" % (name, inv))

wall = b64file("cmd1_wall.b64")     # gzip+base64(wall_new.html)
index = b64file("cmd2_index.b64")   # plain base64(index_new.html)
box = b64file("cmd2_chatbox.b64")   # plain base64(chat_box.html)
redir = b64file("cmd2_redirect.b64")# plain base64(chat_redirect.html)
proxy = b64file("cmd2_proxy.b64")   # plain base64(deepseek_proxy.py v1.1)
print("sizes: wall=%d index=%d box=%d redir=%d proxy=%d" % (len(wall), len(index), len(box), len(redir), len(proxy)))

def chunks(s, n=48000):
    return [s[i:i + n] for i in range(0, len(s), n)]

# ---- cmd0 备份 + 探针（服务器此前零改动，先落备份）----
run("""set -e
mkdir -p /root/sxj_backup_20260831
for f in /var/www/html/wall.html /var/www/html/index.html /var/www/html/chat.html /opt/sxj-chat/deepseek_proxy.py; do
  [ -f "$f" ] && cp -a "$f" /root/sxj_backup_20260831/$(basename $f) || true
done
md5sum /root/sxj_backup_20260831/* || true
systemctl is-active sxj-chat
curl -s http://127.0.0.1:8812/api/models | head -c 200; echo
echo BACKUP_PROBE_OK""", "cmd0_backup_probe")

# ---- wall 分段部署（gzip b64，末段解码校验后替换）----
wc = chunks(wall)
print("wall chunks:", len(wc))
for i, c in enumerate(wc):
    if i == 0:
        pre = "set -e\nrm -f /tmp/wall.b64\ncat > /tmp/wall.b64 <<'SXJB64'\n"
    else:
        pre = "set -e\ncat >> /tmp/wall.b64 <<'SXJB64'\n"
    if i == len(wc) - 1:
        post = """SXJB64
set -e
echo TOTAL $(wc -c < /tmp/wall.b64)
base64 -d /tmp/wall.b64 | gunzip -c > /tmp/wall_new.html
grep -q SXJ-CHATBOX-S /tmp/wall_new.html
grep -q chat_box.html /tmp/wall_new.html
cp /tmp/wall_new.html /var/www/html/wall.html
chmod 644 /var/www/html/wall.html
rm -f /tmp/wall.b64 /tmp/wall_new.html
echo WALL_DEPLOYED $(wc -c < /var/www/html/wall.html)
md5sum /var/www/html/wall.html"""
    else:
        post = "SXJB64\necho APPEND_OK $(wc -c < /tmp/wall.b64)\n"
    run(pre + c + "\n" + post, "wall_p%d" % (i + 1))

# ---- index 分段部署（plain b64）----
ic = chunks(index)
print("index chunks:", len(ic))
for i, c in enumerate(ic):
    if i == 0:
        pre = "set -e\nrm -f /tmp/index.b64\ncat > /tmp/index.b64 <<'SXJB64'\n"
    else:
        pre = "set -e\ncat >> /tmp/index.b64 <<'SXJB64'\n"
    if i == len(ic) - 1:
        post = """SXJB64
set -e
echo TOTAL $(wc -c < /tmp/index.b64)
base64 -d /tmp/index.b64 > /tmp/index_new.html
grep -q 'action="wall.html"' /tmp/index_new.html
cp /tmp/index_new.html /var/www/html/index.html
chmod 644 /var/www/html/index.html
rm -f /tmp/index.b64 /tmp/index_new.html
echo INDEX_DEPLOYED $(wc -c < /var/www/html/index.html)"""
    else:
        post = "SXJB64\necho APPEND_OK $(wc -c < /tmp/index.b64)\n"
    run(pre + c + "\n" + post, "index_p%d" % (i + 1))

# ---- 收尾：chat_box.html + chat.html 重定向 + proxy v1.1 + 重启 + 本机验证 ----
run("""set -e
echo '%s' | base64 -d > /var/www/html/chat_box.html
chmod 644 /var/www/html/chat_box.html
echo '%s' | base64 -d > /var/www/html/chat.html
chmod 644 /var/www/html/chat.html
cp -a /opt/sxj-chat/deepseek_proxy.py /root/sxj_backup_20260831/deepseek_proxy.py.pre_v11 2>/dev/null || true
echo '%s' | base64 -d > /opt/sxj-chat/deepseek_proxy.py
python3 -m py_compile /opt/sxj-chat/deepseek_proxy.py && echo PYOK
systemctl restart sxj-chat
sleep 2
systemctl is-active sxj-chat || { journalctl -u sxj-chat -n 40 --no-pager; exit 31; }
curl -s http://127.0.0.1:8812/api/models | head -c 300; echo
echo CHATBOX $(curl -s http://127.0.0.1/chat_box.html | grep -c sxj_box_sid)
echo WALLMARK $(curl -s http://127.0.0.1/wall.html | grep -c SXJ-CHATBOX-S)
echo REDIR $(curl -s http://127.0.0.1/chat.html | grep -c 'meta http-equiv')
echo IDX $(curl -s http://127.0.0.1/index.html | grep -c 'action=\\"wall.html\\"')
echo FINALIZE_DONE""" % (box, redir, proxy), "cmd_final")
print("ALL_DEPLOY_STEPS_DONE")
