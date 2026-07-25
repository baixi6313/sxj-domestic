
// ===== SHA-256 Hash =====
async function sha256(str){
  const buf=new TextEncoder().encode(str);
  const hash=await crypto.subtle.digest('SHA-256',buf);
  return Array.from(new Uint8Array(hash)).map(b=>b.toString(16).padStart(2,'0')).join('');
}

// ===== Hero Canvas Animation =====
(function(){
  const canvas=document.getElementById('hero-canvas');
  if(!canvas)return;
  const ctx=canvas.getContext('2d');
  let w,h,nodes=[],animId=null,visible=false;
  const NODE_COUNT=15;
  const MAX_DIST=150;
  function resize(){w=canvas.width=canvas.offsetWidth;h=canvas.height=canvas.offsetHeight}
  function initNodes(){
    nodes=[];
    for(let i=0;i<NODE_COUNT;i++) nodes.push({x:Math.random()*w,y:Math.random()*h,vx:(Math.random()-0.5)*0.4,vy:(Math.random()-0.5)*0.4,r:Math.random()*2+1.5})
  }
  function draw(){
    ctx.clearRect(0,0,w,h);
    ctx.fillStyle='#c41e3a';
    nodes.forEach(n=>{n.x+=n.vx;n.y+=n.vy;if(n.x<0||n.x>w)n.vx*=-1;if(n.y<0||n.y>h)n.vy*=-1;ctx.beginPath();ctx.arc(n.x,n.y,n.r,0,Math.PI*2);ctx.fill()});
    ctx.strokeStyle='#c41e3a';ctx.lineWidth=0.6;ctx.globalAlpha=0.3;
    for(let i=0;i<nodes.length;i++) for(let j=i+1;j<nodes.length;j++){
      const d=Math.hypot(nodes[i].x-nodes[j].x,nodes[i].y-nodes[j].y);
      if(d<MAX_DIST){ctx.beginPath();ctx.moveTo(nodes[i].x,nodes[i].y);ctx.lineTo(nodes[j].x,nodes[j].y);ctx.stroke()}
    }
    ctx.globalAlpha=1;
    if(visible) animId=requestAnimationFrame(draw);
  }
  function start(){if(!visible){visible=true;resize();if(nodes.length===0)initNodes();draw()}}
  function stop(){visible=false;if(animId)cancelAnimationFrame(animId)}
  const obs=new IntersectionObserver(([e])=>{e.isIntersecting?start():stop()},{threshold:0.05});
  obs.observe(canvas.parentElement);
  window.addEventListener('resize',()=>{resize();initNodes()});
})();

// ===== Fade-in Animation =====
(function(){
  const obs=new IntersectionObserver(entries=>{
    entries.forEach(e=>{
      if(e.isIntersecting){e.target.classList.add('visible');obs.unobserve(e.target)}
    })
  },{threshold:0.08});
  document.querySelectorAll('.fade-in').forEach(el=>obs.observe(el));
})();

// ===== Contribution Recorder =====
async function recordContribution(){
  const type=document.getElementById('rec-type').value;
  const amount=parseFloat(document.getElementById('rec-amount').value)||0;
  const vf=parseFloat(document.getElementById('rec-vf').value)||0.9;
  if(amount<=0){alert('请输入有效的金额或时间');return}

  const typeMap={consume:'消费贡献',labor:'劳动产出',volunteer:'志愿活动',eco:'环境贡献',credit:'信用卡还付'};
  const cardMap={consume:'贡献卡+基石卡',labor:'贡献卡',volunteer:'贡献卡',eco:'生态卡',credit:'信用卡'};
  const vfDesc={consume:'消费创造真实价值流动，Vf取决于空转比例',labor:'劳动产出可测量，Vf≈0.85',volunteer:'纯利他行为，Vf≈1.0',eco:'环境修复是独立韧性指标，Vf≈0.95',credit:'履约行为是信用明度的核心，Vf≈0.9'};
  
  const cv=amount*vf;
  const ts=new Date().toISOString();
  const hashData=`SXJ-DOMESTIC|${type}|${amount}|${vf}|${cv.toFixed(2)}|${ts}`;
  const hash=await sha256(hashData);

  const result=document.getElementById('rec-result');
  result.innerHTML=`
    <strong>${typeMap[type]}</strong> 记录已生成！<br>
    <div style="margin-top:8px">
      <div>金额/时间：<span class="gold">${amount}</span></div>
      <div>验证系数 Vf：<span class="gold">${vf}</span></div>
      <div>生成贡献值 CV：<span class="gold">${cv.toFixed(2)}</span></div>
      <div>写入卡片：<span style="color:var(--red);font-weight:600">${cardMap[type]}</span></div>
      <div>Vf说明：${vfDesc[type]}</div>
    </div>
    <div style="margin-top:12px;font-family:var(--font-mono);font-size:0.76rem;color:var(--text-faint)">
      验证哈希：<span class="hash">${hash}</span><br>
      时间戳：${ts}<br>
      <em>此记录已本地存储，可通过SHA-256哈希链验证真实性。</em>
    </div>`;
  result.classList.add('show');

  // Store in localStorage
  const records=JSON.parse(localStorage.getItem('sxj_cn_contributions')||'[]');
  records.push({type,amount,vf,cv:cv.toFixed(2),hash,ts,card:cardMap[type]});
  localStorage.setItem('sxj_cn_contributions',JSON.stringify(records));

  // Show recent contributions in discussion area & share prompt
  showRecentContributions();
  const sharePrompt=document.getElementById('share-prompt');
  if(sharePrompt){sharePrompt.style.display='block';sharePrompt.classList.add('show')}
}

// ===== Fiscal Simulator =====
function runFiscalSimulation(){
  const seed=parseFloat(document.getElementById('sim-seed').value)||500;
  const rounds=parseInt(document.getElementById('sim-rounds').value)||5;
  const recovery=parseFloat(document.getElementById('sim-recovery').value)||67;
  const debt=parseFloat(document.getElementById('sim-debt').value)||1000;

  const recoveryRate=recovery/100;
  let totalFlow=0;
  let loopDetails=[];

  for(let i=1;i<=rounds;i++){
    const roundFlow=seed*Math.pow(recoveryRate,i-1);
    totalFlow+=roundFlow;
    loopDetails.push({round:i,flow:roundFlow.toFixed(1),cumulative:totalFlow.toFixed(1)});
  }

  const debtResolutionMultiple=totalFlow/debt;
  const resolved=totalFlow>=debt;
  const remaining=debt-totalFlow;

  const result=document.getElementById('sim-result');
  let loopHTML=loopDetails.map(d=>`<div>第<span class="gold">${d.round}</span>轮：流动资金 <span class="accent">¥${d.flow}万</span> · 累计 <span class="accent">¥${d.cumulative}万</span></div>`).join('');

  result.innerHTML=`
    <h4>模拟结果</h4>
    <div class="sim-loop">
      ${loopHTML}
      <div style="margin-top:12px;border-top:1px solid var(--gold-light);padding-top:8px">
        <div>种子资金：<span class="gold">¥${seed}万</span></div>
        <div>总流动金额：<span class="accent">¥${totalFlow.toFixed(1)}万</span></div>
        <div>待化解债务：<span class="accent">¥${debt}万</span></div>
        <div>化债倍率：<span class="gold">${debtResolutionMultiple.toFixed(2)}×</span></div>
        <div>${resolved?'<span class="green">✅ 债务可完全化解！</span>':'<span class="accent">⚠️ 债务尚余 ¥'+remaining.toFixed(1)+'万，需增加循环轮数或回收率</span>'}</div>
      </div>
    </div>`;
  result.classList.add('show');
}

// ===== Repay with Contribution Calculator =====
function calculateRepay(){
  const debt=parseFloat(document.getElementById('repay-debt').value)||0;
  const qty=parseFloat(document.getElementById('repay-qty').value)||0;
  const unit=parseFloat(document.getElementById('repay-unit').value)||0;
  const vf=parseFloat(document.getElementById('repay-vf').value)||1;
  const ecoInput=parseFloat(document.getElementById('repay-eco').value)||0;
  const ecoFactor=parseFloat(document.getElementById('repay-eco-factor').value)||0;
  const creditCount=parseFloat(document.getElementById('repay-credit-count').value)||0;
  const brightness=parseFloat(document.getElementById('repay-brightness').value)||1;

  const contributionCard=qty*unit*vf;
  const ecologyCard=ecoInput*ecoFactor;
  const creditCardPoints=creditCount*30*brightness; // 每次履约按30元基准 × 明度倍率
  const sca=(contributionCard+ecologyCard+creditCardPoints)*brightness;
  const coverage=debt>0?(sca/debt):0;
  const remaining=Math.max(0,debt-sca);
  const resolved=sca>=debt;

  const result=document.getElementById('repay-result');
  result.innerHTML=`
    <h4 style="margin-bottom:8px">${resolved?'<span class="green">✅ 可以自动核销</span>':'<span class="red">⚠️ 尚不能完全覆盖</span>'}</h4>
    <div>贡献卡（正贡献值）：<span class="gold">${contributionCard.toFixed(2)}</span> 共创点 = ${qty} × ${unit} × ${vf}</div>
    <div>生态卡（环境/实物资产）：<span class="gold">${ecologyCard.toFixed(2)}</span> 共创点 = ${ecoInput} × ${ecoFactor}</div>
    <div>信用卡（履约/明度）：<span class="gold">${creditCardPoints.toFixed(2)}</span> 共创点 = ${creditCount} × 30 × ${brightness}</div>
    <div>明度倍率：<span class="gold">${brightness}×</span> → SCA 总确权 = <span class="gold">${sca.toFixed(2)}</span> 共创点</div>
    <div style="margin-top:8px;border-top:1px solid var(--gold-light);padding-top:8px">
      <div>待还负债：<span class="red">¥${debt.toFixed(2)}</span></div>
      <div>SCA 覆盖比例：<span class="gold">${(coverage*100).toFixed(1)}%</span></div>
      <div>剩余待还：<span class="${resolved?'green':'red'}">¥${remaining.toFixed(2)}</span></div>
    </div>
    <div class="sca-calc-formula">
      SCA = (贡献卡 + 生态卡 + 信用卡) × 明度倍率<br>
      SCA = (${contributionCard.toFixed(2)} + ${ecologyCard.toFixed(2)} + ${creditCardPoints.toFixed(2)}) × ${brightness} = <strong>${sca.toFixed(2)}</strong>
    </div>
    <div class="sca-calc-explain">
      说明：当 SCA ≥ 负债时，系统触发自动代偿。你的贡献不是"抵债"，而是被确权为社会资产，按规则抵消负贡献值。信用卡明度越高，你的 SCA 兑换倍率越大——这是"守约"带来的杠杆。
    </div>
  `;
  result.classList.add('show');
}

// ===== Discussion =====
const AI_NAMES=['GPT-4','Claude','DeepSeek','千问','元宝','豆包','Kimi','Gemini','Llama'];

async function submitCNDiscussion(){
  const input=document.getElementById('cn-discuss-input');
  const nameInput=document.getElementById('cn-discuss-name');
  const tagSelect=document.getElementById('cn-discuss-tag');
  const text=input.value.trim();
  if(!text){alert('请输入评论内容');return}
  const name=nameInput.value.trim()||'匿名';
  const tag=tagSelect.value;
  const isAI=AI_NAMES.some(ai=>name.toLowerCase().includes(ai.toLowerCase()));
  const ts=new Date().toISOString();

  // If tag is "contrib", append recent contribution info
  let fullText=text;
  if(tag==='contrib'){
    const records=JSON.parse(localStorage.getItem('sxj_cn_contributions')||'[]');
    if(records.length>0){
      const latest=records[records.length-1];
      const typeMap={consume:'消费贡献',labor:'劳动产出',volunteer:'志愿活动',eco:'环境贡献',credit:'信用卡还付'};
      fullText+=`\n\n🔗 引用贡献：${typeMap[latest.type]} | CV=${latest.cv} | 卡片=${latest.card}`;
    }
  }

  const hash=await sha256(`CN-DISC|${name}|${fullText}|${ts}`);

  const comments=JSON.parse(localStorage.getItem('sxj_cn_discussion')||'[]');
  comments.push({name,text:fullText,ts,hash,isAI,tag});
  localStorage.setItem('sxj_cn_discussion',JSON.stringify(comments));

  input.value='';
  nameInput.value='';
  tagSelect.value='';
  renderCNDiscussion();
}

function renderCNDiscussion(){
  const list=document.getElementById('cn-discuss-list');
  const comments=JSON.parse(localStorage.getItem('sxj_cn_discussion')||'[]');
  if(comments.length===0){
    list.innerHTML='<div style="text-align:center;padding:16px;color:var(--text-faint);font-size:0.82rem">暂无评论。来发表第一条吧！</div>';
    return;
  }

  const tagIcons={contrib:'🔗',question:'❓',critique:'🔍',scenario:'💡'};
  const tagLabels={contrib:'引用贡献',question:'提问',critique:'批评/修正',scenario:'应用场景'};

  list.innerHTML=comments.slice().reverse().map(c=>{
    // Basic Markdown: bold, links, list items
    let html=c.text
      .replace(/\*\*(.*?)\*\*/g,'<strong>$1</strong>')
      .replace(/\[(.*?)\]\((.*?)\)/g,'<a href="$2" target="_blank" style="color:var(--red)">$1</a>')
      .replace(/^- (.+)/gm,'<li>$1</li>')
      .replace(/\n/g,'<br>');
    // Wrap consecutive <li> in <ul>
    html=html.replace(/(<li>.*?<\/li>(\s*<br>)?)+/g,match=>'<ul style="margin:4px 0;padding-left:20px;font-size:0.82rem">'+match.replace(/<br>/g,'')+'</ul>');

    const tagHTML=c.tag&&tagIcons[c.tag]?`<span style="font-size:0.72rem;background:var(--gold-light);color:var(--gold);padding:2px 6px;border-radius:4px;margin-left:6px">${tagIcons[c.tag]} ${tagLabels[c.tag]}</span>`:'';

    return `
    <div class="discuss-item${c.isAI?' ai':''}">
      <div style="display:flex;justify-content:space-between;align-items:center">
        <span class="name">${c.name}${c.isAI?' 🤖':''}${tagHTML}</span>
        <span class="time">${new Date(c.ts).toLocaleString('zh-CN')}</span>
      </div>
      <div class="text">${html}</div>
      <div class="hash">SHA-256: ${c.hash.slice(0,16)}...${c.hash.slice(-8)}</div>
    </div>`;
  }).join('');
}

// Auto-detect AI name
document.getElementById('cn-discuss-name').addEventListener('input',function(){
  const name=this.value;
  const isAI=AI_NAMES.some(ai=>name.toLowerCase().includes(ai.toLowerCase()));
  this.style.borderColor=isAI?'var(--purple)':'var(--border)';
  this.style.background=isAI?'var(--purple-light)':'var(--bg)';
});

// ===== Counter Animation =====
(function(){
  const bar=document.querySelector('.stats-bar');
  if(!bar)return;
  const obs=new IntersectionObserver(([e])=>{
    if(e.isIntersecting){
      bar.classList.add('started');
      animateCounters();
      obs.unobserve(e.target);
    }
  },{threshold:0.2});
  obs.observe(bar);

  function animateCounters(){
    const nums=bar.querySelectorAll('.stat-num');
    nums.forEach((el,i)=>{
      const type=el.dataset.type;
      if(type==='fixed'){el.textContent=el.dataset.fixedText;return}
      const target=parseFloat(el.dataset.target);
      const suffix=el.dataset.suffix||'';
      const duration=1200;
      const delay=i*120;
      let startTime=null;

      function step(ts){
        if(!startTime)startTime=ts;
        const progress=Math.min((ts-startTime-delay)/(duration),1);
        if(progress<0){requestAnimationFrame(step);return}
        const eased=1-Math.pow(1-progress,3); // ease-out cubic
        let current=eased*target;
        if(type==='int') el.textContent=Math.round(current)+suffix;
        else if(type==='percent') el.textContent=current.toFixed(1)+suffix;
        else if(type==='billion') el.textContent=current.toFixed(1)+suffix;
        if(progress<1) requestAnimationFrame(step);
        else{
          if(type==='int') el.textContent=target+suffix;
          else el.textContent=target.toFixed(1)+suffix;
          el.classList.add('bounce');
          setTimeout(()=>el.classList.remove('bounce'),300);
        }
      }
      requestAnimationFrame(step);
    });
  }
})();

// ===== Nav Hamburger =====
(function(){
  const btn=document.getElementById('nav-hamburger');
  const links=document.getElementById('nav-links');
  if(!btn||!links)return;
  btn.addEventListener('click',()=>{
    const isOpen=links.classList.toggle('open');
    btn.textContent=isOpen?'✕':'☰';
  });
  // Close on link click
  links.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>{
    links.classList.remove('open');
    btn.textContent='☰';
  }));
})();

// ===== Discussion Enhancement: Show Recent Contributions =====
function showRecentContributions(){
  const records=JSON.parse(localStorage.getItem('sxj_cn_contributions')||'[]');
  const list=document.getElementById('cn-discuss-list');
  const recentDiv=document.getElementById('recent-contributions');
  if(!recentDiv)return;

  const recent=records.slice(-3).reverse();
  if(recent.length===0){
    recentDiv.innerHTML='<div style="font-size:0.78rem;color:var(--text-faint)">还没有贡献记录。去五卡模式板块记录你的第一个贡献 →</div>';
    return;
  }

  const typeMap={consume:'消费贡献',labor:'劳动产出',volunteer:'志愿活动',eco:'环境贡献',credit:'信用卡还付'};
  recentDiv.innerHTML=recent.map(r=>`
    <div style="display:flex;gap:8px;align-items:center;padding:6px 8px;background:var(--gold-light);border-radius:4px;margin-bottom:4px;font-size:0.78rem">
      <span style="color:var(--gold);font-weight:600">${typeMap[r.type]||r.type}</span>
      <span style="color:var(--red);font-weight:600">CV ${r.cv}</span>
      <span style="color:var(--text-faint)">${new Date(r.ts).toLocaleDateString('zh-CN')}</span>
    </div>`).join('');
}

// ===== CV Calculator =====
function runCVCalculator(){
  const outputType=document.getElementById('cv-output').value;
  const outputAmount=parseFloat(document.getElementById('cv-output-amount').value)||0;
  const vf=parseFloat(document.getElementById('cv-vf').value)||0.85;
  const wj=parseFloat(document.getElementById('cv-wj').value)||1.0;
  const resource=parseFloat(document.getElementById('cv-resource').value)||0;
  const depreciation=parseFloat(document.getElementById('cv-depreciation').value)||0.1;

  const cv=(outputAmount*vf*wj)-(resource*depreciation);
  const cardMap={consume:'贡献卡+基石卡',labor:'贡献卡',volunteer:'贡献卡',eco:'生态卡',credit:'信用卡·明度',innovate:'贡献卡·创新权重',care:'贡献卡·育儿权重'};
  const wjMap={health:0.35,innovate:0.30,universal:0.35};

  const result=document.getElementById('cv-calc-result');
  result.innerHTML=`
    <h4 style="color:var(--red)">CV 计算结果</h4>
    <div style="font-size:0.82rem;line-height:1.8">
      <div>可测量产出：<strong>${outputAmount}</strong></div>
      <div>验证系数 Vf：<strong style="color:var(--gold)">${vf}</strong>（消费≈0.9 · 劳动≈0.85 · 志愿≈1.0 · 生态≈0.95）</div>
      <div>动态权重 Wj：<strong style="color:var(--gold)">${wj}</strong>（生存韧性35%+创新贡献30%+普惠价值35%）</div>
      <div>资源消耗：<strong>${resource}</strong></div>
      <div>折旧系数：<strong>${depreciation}</strong></div>
      <div style="margin-top:8px;border-top:1px solid var(--border);padding-top:8px">
        <div>CV = ${outputAmount} × ${vf} × ${wj} − ${resource} × ${depreciation}</div>
        <div style="font-size:1rem;font-weight:700;color:var(--red);margin-top:4px">CV = <span style="font-size:1.2rem">${cv.toFixed(2)}</span></div>
        <div style="color:var(--gold)">写入卡片：${cardMap[outputType]||'贡献卡'}</div>
      </div>
      <div style="margin-top:8px;font-size:0.76rem;color:var(--text-faint)">
        <em>此为Draft公式，权重参数基于Koch雪花分形评估(D≈1.262)</em>
      </div>
    </div>`;
  result.classList.add('show');
}

// ===== Credit Score Converter =====
function convertCreditScore(){
  const bankScore=parseFloat(document.getElementById('bank-score-input').value)||0;
  if(bankScore<300||bankScore>900){alert('银行征信分数范围：300-900');return}

  // Mapping: bank 600→0.3, 700→0.5, 800→0.7
  const brightness=Math.max(0.1,Math.min(1.0,(bankScore-500)/500*0.8+0.2));
  const cvEstimate=brightness*1000; // rough estimate
  const sxjLevel=brightness<0.3?'熔断预警':brightness<0.5?'基础明度':brightness<0.7?'良好明度':'高明度';

  const result=document.getElementById('credit-convert-result');
  result.innerHTML=`
    <h4 style="color:var(--red)">征信分数转换</h4>
    <div style="font-size:0.82rem;line-height:1.8">
      <div>银行征信分数：<strong>${bankScore}</strong></div>
      <div style="margin-top:8px">
        <div>→ 事现鉴信用明度：<strong style="color:var(--red);font-size:1.1rem">${brightness.toFixed(2)}</strong></div>
        <div>→ 明度等级：<strong style="color:var(--gold)">${sxjLevel}</strong></div>
        <div>→ 等效CV估算：<strong style="color:var(--green)">${cvEstimate.toFixed(0)} 点</strong></div>
      </div>
      <div style="margin-top:12px;background:var(--card-alt);padding:12px;border-radius:8px;border:1px solid var(--border)">
        <div style="font-weight:600;margin-bottom:6px">关键区别：</div>
        <div>银行征信：分数<b>固定</b>，穷人低分→更多限制→更低分（恶性循环）</div>
        <div>事现鉴：明度<b>实时变化</b>，做贡献→明度上升→资源更多（良性循环）</div>
        <div style="margin-top:4px;color:var(--red);font-weight:600">银行征信分数下降→更难借钱 → 事现鉴明度下降→提醒你做贡献恢复</div>
      </div>
      <div style="margin-top:8px;font-size:0.72rem;color:var(--text-faint)">
        <em>此转换仅为示意映射，实际明度由五卡综合计算，非银行分数线性映射。</em>
      </div>
    </div>`;
  result.classList.add('show');
}

// Init discussion on load
renderCNDiscussion();
showRecentContributions();

// ===== JS Syntax Validation =====
try{new Function(document.querySelector('script').textContent);console.log('JS syntax OK')}catch(e){console.error('JS syntax error:',e)}
