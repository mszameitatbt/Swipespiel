let loggedIn=false;

const $=id=>document.getElementById(id);
async function api(url, opts={}) {
  const r=await fetch(url,{...opts,headers:{"Content-Type":"application/json",...(opts.headers||{})}});
  const d=await r.json();
  if(r.status===403){loggedIn=false; showLogin(); throw new Error("Nicht autorisiert");}
  if(!d.ok && r.status>=400) throw new Error(d.error||"Fehler");
  return d;
}
function showLogin(){ $("login").classList.remove("hidden"); $("dashboard").classList.add("hidden"); }
function showDash(){ $("login").classList.add("hidden"); $("dashboard").classList.remove("hidden"); }

async function login(){
  try{
    await api("/api/admin/login",{method:"POST",body:JSON.stringify({pin:$("pin").value})});
    loggedIn=true; showDash(); refresh();
  }catch(e){$("loginError").textContent=e.message}
}
$("loginBtn").onclick=login;
$("pin").addEventListener("keydown",e=>{if(e.key==="Enter")login()});

$("logoutBtn").onclick=async()=>{await api("/api/admin/logout",{method:"POST"});showLogin()};
$("startBtn").onclick=async()=>{await api("/api/admin/start",{method:"POST"});refresh()};
$("openBtn").onclick=async()=>{await api("/api/admin/open",{method:"POST"});refresh()};
$("closeBtn").onclick=async()=>{await api("/api/admin/close",{method:"POST"});refresh()};
$("revealBtn").onclick=async()=>{await api("/api/admin/reveal",{method:"POST"});refresh()};
$("nextBtn").onclick=async()=>{try{await api("/api/admin/next",{method:"POST"});refresh()}catch(e){alert(e.message)}};
$("round2Btn").onclick=async()=>{if(confirm("Runde 2 starten? Die individuelle Verbindung zur ersten Runde wird nicht gespeichert.")){await api("/api/admin/start_round2",{method:"POST"});refresh()}};
$("resetBtn").onclick=async()=>{if(confirm("Alle Abstimmungsergebnisse und Sessiondaten löschen?")){await api("/api/admin/reset",{method:"POST"});refresh()}};

function render(s){
  $("round").textContent=`RUNDE ${s.round}`;
  $("qNumber").textContent=s.question?`AUSSAGE ${s.question.id} · ${s.question_index+1}/${s.question_count}`:"–";
  $("qText").textContent=s.question?`„${s.question.text}“`:"Noch keine Session gestartet.";
  $("qHint").textContent=s.question?.hint||"";
  $("total").textContent=`${s.votes?.total||0} Antworten`;
  $("statusText").textContent=!s.active?"Inaktiv":s.accepting?"Abstimmung läuft":s.revealed?"Ergebnis angezeigt":"Bereit";
  $("statusDot").classList.toggle("live",s.accepting);
  const yes=s.votes?.yes||0,no=s.votes?.no||0,total=yes+no,yp=total?Math.round(yes/total*100):0;
  $("yesPercent").textContent=total?`${yp}%`:"–";
  $("teacherYes").textContent=yes;$("teacherNo").textContent=no;
  $("teacherYesBar").style.width=`${yp}%`;
}

async function refresh(){
  if(!loggedIn)return;
  try{
    const s=await api("/api/admin/state"); render(s); await renderSummary();
  }catch(e){}
}
async function renderSummary(){
  const d=await api("/api/admin/summary");
  $("summary").innerHTML=`<div class="summary-row summary-head"><div>AUSSAGE</div><div>RUNDE 1</div><div>RUNDE 2</div></div>`+
  d.questions.map(x=>{
    const p1=x.round1.total?Math.round(x.round1.yes/x.round1.total*100):0;
    const p2=x.round2.total?Math.round(x.round2.yes/x.round2.total*100):0;
    return `<div class="summary-row"><div>${x.question.id}. ${x.question.text}</div>
      <div>${p1}% JA<div class="mini-bar"><i style="width:${p1}%"></i></div></div>
      <div>${p2}% JA<div class="mini-bar"><i style="width:${p2}%"></i></div></div></div>`;
  }).join("");
  $("scoreGrid").innerHTML="";
  for(let i=0;i<=10;i++){
    const b=document.createElement("button");b.textContent=i;b.onclick=()=>submitScore(i);$("scoreGrid").appendChild(b);
  }
  $("scoreAverage").textContent=d.score_average===null?"Noch keine Bewertungen":`Klassenmittel: ${d.score_average}/10 (${d.scores.length} Stimmen)`;
}
async function submitScore(score){
  try{await api("/api/admin/final-score",{method:"POST",body:JSON.stringify({score})});renderSummary()}catch(e){alert(e.message)}
}
setInterval(refresh,1000);
