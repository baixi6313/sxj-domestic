(function(){
if(window.__CVW__)return;window.__CVW__=1;
var CSS='#cvw-btn{position:fixed;right:16px;bottom:16px;z-index:99990;background:#1a1a2e;color:#fff;padding:8px 14px;border-radius:20px;font-size:13px;cursor:pointer;box-shadow:0 2px 8px rgba(0,0,0,.25);font-family:system-ui,sans-serif}#cvw-pnl{position:fixed;right:16px;bottom:56px;z-index:99991;width:340px;max-width:92vw;max-height:70vh;overflow:auto;background:#fff;border:1px solid #e5e5ef;border-radius:12px;box-shadow:0 8px 30px rgba(0,0,0,.18);font-family:system-ui,sans-serif;font-size:13px;color:#1a1a2e;display:none}#cvw-pnl .h{display:flex;justify-content:space-between;align-items:center;padding:10px 14px;border-bottom:1px solid #eef;font-weight:700}#cvw-pnl .h a{font-size:12px;color:#4a4ae0;text-decoration:none;font-weight:400}#cvw-pnl .x{cursor:pointer;color:#999;padding:0 4px}#cvw-pnl table{width:100%;border-collapse:collapse;font-size:12px}#cvw-pnl th,#cvw-pnl td{padding:6px 10px;text-align:left;border-bottom:1px solid #f0f0f6}#cvw-pnl th{color:#888;font-weight:500;font-size:11px}#cvw-pnl .num{text-align:right;font-variant-numeric:tabular-nums}.cvw-pos{color:#0a7d43;font-weight:700}.cvw-neg{color:#b3261e;font-weight:700}#cvw-pnl .recs{padding:8px 14px;font-size:11px;color:#777;line-height:1.7;border-top:1px solid #eef}#cvw-pnl .f{padding:10px 14px;border-top:1px solid #eef;background:#fafaff}#cvw-pnl .f input,#cvw-pnl .f textarea{width:100%;box-sizing:border-box;margin:3px 0 8px;padding:6px 8px;border:1px solid #ddd;border-radius:6px;font-size:12px;font-family:inherit}#cvw-pnl .f button{background:#1a1a2e;color:#fff;border:none;border-radius:6px;padding:7px 16px;font-size:12px;cursor:pointer}#cvw-pnl .f .msg{font-size:11px;margin-top:6px}#cvw-pnl .f .ok{color:#0a7d43}#cvw-pnl .f .er{color:#b3261e}';
var st=document.createElement('style');st.textContent=CSS;document.head.appendChild(st);
var btn=document.createElement('div');btn.id='cvw-btn';btn.textContent='CV 榜';
var pnl=document.createElement('div');pnl.id='cvw-pnl';
pnl.innerHTML='<div class="h"><span>事现鉴 CV 榜</span><span><a href="/cv.html" target="_blank">详情页</a> <span class="x" id="cvw-x">✕</span></span></div><div id="cvw-body">加载中…</div>';
document.body.appendChild(btn);document.body.appendChild(pnl);
function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[c]})}
function render(d){
 var acs=Object.keys(d.accounts||{}).map(function(k){var a=d.accounts[k];a.k=k;return a});
 acs.sort(function(x,y){return y.cv_net-x.cv_net});
 var rows=acs.map(function(a,i){var c=a.cv_net>0?'cvw-pos':(a.cv_net<0?'cvw-neg':'');
  return '<tr><td>'+(i+1)+'</td><td style="font-family:monospace;font-size:11px">'+esc(a.k)+'</td><td class="num">'+a.GzzB+'</td><td class="num">'+a.GzzC+'</td><td class="num '+c+'">'+(a.cv_net>0?'+':'')+a.cv_net+'</td></tr>'}).join('');
 var recs=((d.meta&&d.meta.records)||[]).slice(-3).reverse().map(function(r){return '· '+esc(r.code)+' '+esc(String(r.reason||'').slice(0,40))}).join('<br>');
 var tok=null;try{tok=localStorage.getItem('sxj_token')}catch(e){}
 var form='';
 if(tok){form='<div class="f"><b style="font-size:12px">白玺实时记录（考核以CV为准）</b><input id="cvw-acc" placeholder="账户 Gzz-A-码（如 Gzz-A-Coze-CN-Li）"><input id="cvw-b" placeholder="GzzB 变动（整数，如 100）"><input id="cvw-c" placeholder="GzzC 扣减（整数，如 -300，记为扣减量300）"><textarea id="cvw-r" rows="2" placeholder="理由（必填）"></textarea><button id="cvw-go">落账并更新榜单</button><div class="msg" id="cvw-msg"></div></div>';}
 else{form='<div class="f" style="font-size:11px;color:#888">CV考核裁定以白玺登录身份记录。<a href="/login_v2.html" target="_blank">白玺登录</a>后可在本面板实时记录。</div>';}
 document.getElementById('cvw-body').innerHTML='<table><tr><th>#</th><th>账户(Gzz-A)</th><th class="num">GzzB</th><th class="num">GzzC</th><th class="num">CV净值</th></tr>'+(rows||'<tr><td colspan="5">暂无</td></tr>')+'</table><div class="recs">'+(recs||'')+'</div>'+form;
 var go=document.getElementById('cvw-go');
 if(go)go.onclick=function(){
  var acc=document.getElementById('cvw-acc').value.trim();
  var b=document.getElementById('cvw-b').value.trim()||'0';
  var c=document.getElementById('cvw-c').value.trim()||'0';
  var r=document.getElementById('cvw-r').value.trim();
  var msg=document.getElementById('cvw-msg');msg.className='msg';msg.textContent='提交中…';
  fetch('/api/cv/record',{method:'POST',headers:{'Content-Type':'application/json','Authorization':'Bearer '+tok},body:JSON.stringify({account:acc,gzzb_delta:parseInt(b,10),gzzc_delta:parseInt(c,10),reason:r})}).then(function(x){return x.json()}).then(function(j){
   if(j.ok){msg.className='msg ok';msg.textContent='已落账：'+(j.codes||[]).join('，')+'（'+acc+' CV净值 '+(j.cv_net>0?'+':'')+j.cv_net+'）';load();}
   else{msg.className='msg er';msg.textContent='失败：'+(j.error||'未知错误');}}).catch(function(e){msg.className='msg er';msg.textContent='网络错误';});
 };
}
function load(){fetch('/data/cv_ledger.json?ts='+Date.now()).then(function(r){return r.json()}).then(render).catch(function(){document.getElementById('cvw-body').textContent='数据加载失败'});}
btn.onclick=function(){var p=pnl.style;p.display=p.display==='none'?'block':'none';if(p.display==='block')load();};
document.addEventListener('click',function(e){if(e.target.id==='cvw-x')pnl.style.display='none';});
setInterval(function(){if(pnl.style.display==='block')load();},60000);
})();
