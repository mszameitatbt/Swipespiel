let loggedIn=false;
const $=id=>document.getElementById(id);

async function api(url, opts={}){
  const r=await fetch(url,{
    ...opts,
    headers:{"Content-Type":"application/json",...(opts.headers||{})}
  });
  const d=await r.json();
  if(r.status===403){
    loggedIn=false;
    showLogin();
    throw new Error("Nicht autorisiert");
  }
  if(!d.ok && r.status>=400) throw new Error(d.error||"Fehler");
  return d;
}

function showLogin(){
  $("login").classList.remove("hidden");
  $("dashboard").classList.add("hidden");
}

function showDash(){
  $("login").classList.add("hidden");
  $("dashboard").classList.remove("hidden");
}

async function login(){
  try{
    await api("/api/admin/login",{
      method:"POST",
      body:JSON.stringify({pin:$("pin").value})
    });
    loggedIn=true;
    showDash();
    refresh();
  }catch(e){
    $("loginError").textContent=e.message;
  }
}

$("loginBtn").onclick=login;
$("pin").addEventListener("keydown",e=>{
  if(e.key==="Enter")login()
});

$("logoutBtn").onclick=async()=>{
  await api("/api/admin/logout",{method:"POST"});
  showLogin();
};

$("startBtn").onclick=async()=>{
  await api("/api/admin/start",{method:"POST"});
  refresh();
};

$("openBtn").onclick=async()=>{
  await api("/api/admin/open",{method:"POST"});
  refresh();
};

$("closeBtn").onclick=async()=>{
  await api("/api/admin/close",{method:"POST"});
  refresh();
};

$("revealBtn").onclick=async()=>{
  await api("/api/admin/reveal",{method:"POST"});
  refresh();
};

$("nextBtn").onclick=async()=>{
  try{
    await api("/api/admin/next",{method:"POST"});
    refresh();
  }catch(e){
    alert(e.message);
  }
};

$("constitutionStartBtn").onclick=async()=>{
  if(!confirm(
    "Verfassungsbau starten? Die zwölf Swipe-Aussagen bleiben gespeichert, " +
    "aber danach beginnt die neue Vorschlagsphase."
  )) return;

  await api("/api/admin/start_constitution",{method:"POST"});
  refresh();
};

$("closeSubmissionsBtn").onclick=async()=>{
  await api("/api/admin/submissions/close",{method:"POST"});
  refresh();
};

$("openProposalBtn").onclick=async()=>{
  try{
    await api("/api/admin/proposal/open",{method:"POST"});
    refresh();
  }catch(e){
    alert(e.message);
  }
};

$("closeProposalBtn").onclick=async()=>{
  await api("/api/admin/proposal/close",{method:"POST"});
  refresh();
};

$("revealProposalBtn").onclick=async()=>{
  await api("/api/admin/proposal/reveal",{method:"POST"});
  refresh();
};

$("acceptProposalBtn").onclick=async()=>{
  try{
    await api("/api/admin/proposal/accept",{method:"POST"});
    refresh();
  }catch(e){
    alert(e.message);
  }
};

$("releaseComparisonBtn").onclick=async()=>{
  await api("/api/admin/release_comparison",{method:"POST"});
  refresh();
};

$("rejectProposalBtn").onclick=async()=>{
  if(!confirm("Diesen Vorschlag wirklich nicht in die Klassenverfassung aufnehmen?")) return;

  await api("/api/admin/proposal/reject",{method:"POST"});
  refresh();
};

$("resetBtn").onclick=async()=>{
  if(confirm("Alle Abstimmungsergebnisse, Vorschläge und Sessiondaten löschen?")){
    await api("/api/admin/reset",{method:"POST"});
    refresh();
  }
};

function render(s){
  $("phase").textContent =
    s.phase === "constitution" ? "VERFASSUNGSBAU" : "RUNDE 1";

  if(s.phase === "constitution"){
    renderConstitution(s);
  }else{
    renderRound1(s);
  }
}

function renderRound1(s){
  $("qNumber").textContent =
    s.question ? `AUSSAGE ${s.question.id} · ${s.question_index+1}/${s.question_count}` : "–";
  $("qText").textContent =
    s.question ? `„${s.question.text}“` : "Noch keine Session gestartet.";

  $("total").textContent=`${s.votes?.total||0} Antworten`;
  $("statusText").textContent =
    !s.active ? "Inaktiv" :
    s.accepting ? "Abstimmung läuft" :
    s.revealed ? "Ergebnis angezeigt" : "Bereit";

  $("statusDot").classList.toggle("live",s.accepting);

  const yes=s.votes?.yes||0;
  const no=s.votes?.no||0;
  const total=yes+no;
  const yp=total?Math.round(yes/total*100):0;

  $("yesPercent").textContent=total?`${yp}%`:"–";
  $("teacherYes").textContent=yes;
  $("teacherNo").textContent=no;
  $("teacherYesBar").style.width=`${yp}%`;

  $("constitutionControls").classList.add("hidden");
  $("constitutionLive").classList.add("hidden");

  $("openBtn").classList.remove("hidden");
  $("closeBtn").classList.remove("hidden");
  $("revealBtn").classList.remove("hidden");
  $("nextBtn").classList.remove("hidden");
  $("constitutionStartBtn").classList.remove("hidden");
}

function renderConstitution(s){
  $("qNumber").textContent="VERFASSUNGSBAU";
  $("qText").textContent="Die Klasse entwirft Schritt für Schritt ihre eigene Verfassung.";
  $("qHint").textContent="Erst eigene Regeln entwickeln, dann mit der historischen Verfassung von 1791 vergleichen.";
  $("total").textContent =
    `${(s.proposals||[]).filter(p=>p.status==="pending").length} offene Vorschläge`;

  $("statusText").textContent =
    s.proposal_accepting ? "Abstimmung läuft" :
    s.proposal_revealed ? "Ergebnis angezeigt" :
    s.submission_open ? "Vorschläge werden gesammelt" : "Vorschläge geschlossen";

  $("statusDot").classList.toggle("live",s.proposal_accepting);

  const yes=s.proposal_votes?.yes||0;
  const no=s.proposal_votes?.no||0;
  const total=yes+no;
  const yp=total?Math.round(yes/total*100):0;

  $("yesPercent").textContent=total?`${yp}%`:"–";
  $("teacherYes").textContent=yes;
  $("teacherNo").textContent=no;
  $("teacherYesBar").style.width=`${yp}%`;

  $("openBtn").classList.add("hidden");
  $("closeBtn").classList.add("hidden");
  $("revealBtn").classList.add("hidden");
  $("nextBtn").classList.add("hidden");
  $("constitutionStartBtn").classList.add("hidden");

  $("constitutionControls").classList.remove("hidden");
  $("constitutionLive").classList.remove("hidden");

  $("submissionStatus").textContent =
    s.submission_open ? "● offen" : "● geschlossen";

  renderProposalQueue(s.proposals||[]);
  renderCurrentProposal(s.current_proposal,s.proposal_accepting,s.proposal_revealed);
  renderProposalResult(s.proposal_votes||{yes:0,no:0,total:0},s.proposal_revealed);
  renderConstitutionRules(s.constitution_rules||[]);

  $("releaseComparisonBtn").disabled = !s.active;
  $("comparisonArea").classList.toggle("hidden", !s.comparison_released);

  if(s.comparison_released){
    renderActualRules(s.actual_constitution||[]);
  }
}

function renderProposalQueue(proposals){
  const pending=proposals.filter(p=>p.status==="pending");

  if(!pending.length){
    $("proposalQueue").innerHTML =
      `<div class="empty-state">Noch keine offenen Vorschläge.</div>`;
    return;
  }

  $("proposalQueue").innerHTML = pending.map(p=>`
    <div class="proposal-row">
      <div class="proposal-row-text">${escapeHtml(p.text)}</div>
      <button class="secondary" onclick="selectProposal(${p.id})">Anzeigen</button>
    </div>
  `).join("");
}

async function selectProposal(id){
  try{
    await api("/api/admin/proposal/select",{
      method:"POST",
      body:JSON.stringify({id})
    });
    refresh();
  }catch(e){
    alert(e.message);
  }
}

function renderCurrentProposal(proposal,accepting,revealed){
  if(!proposal){
    $("currentProposalTitle").textContent="Noch kein Vorschlag ausgewählt";
    $("currentProposal").textContent="Wähle links einen Vorschlag aus.";
    $("openProposalBtn").disabled=true;
    $("closeProposalBtn").disabled=true;
    $("revealProposalBtn").disabled=true;
    $("acceptProposalBtn").disabled=true;
    $("rejectProposalBtn").disabled=true;
    return;
  }

  $("currentProposalTitle").textContent=`Vorschlag ${proposal.id}`;
  $("currentProposal").textContent=`„${proposal.text}“`;

  $("openProposalBtn").disabled=accepting || revealed;
  $("closeProposalBtn").disabled=!accepting;
  $("revealProposalBtn").disabled=!accepting && !revealed;
  $("acceptProposalBtn").disabled=!revealed;
  $("rejectProposalBtn").disabled=!revealed;
}

function renderProposalResult(votes,revealed){
  const yes=votes.yes||0;
  const no=votes.no||0;
  const total=yes+no;
  const yp=total?Math.round(yes/total*100):0;

  $("proposalYesPercent").textContent=total?`${yp}%`:"–";
  $("proposalYes").textContent=yes;
  $("proposalNo").textContent=no;
  $("proposalYesBar").style.width=`${yp}%`;
}

function renderConstitutionRules(rules){
  if(!rules.length){
    $("constitutionRules").innerHTML =
      `<div class="empty-state">Noch keine Regel beschlossen.</div>`;
    return;
  }

  $("constitutionRules").innerHTML=rules.map(r=>`
    <div class="constitution-rule">
      <strong>${r.number}.</strong>
      <span>${escapeHtml(r.text)}</span>
    </div>
  `).join("");
}

function renderActualRules(rules){
  $("actualRules").innerHTML=rules.map(r=>`
    <div class="actual-rule">
      <div class="actual-rule-title">${escapeHtml(r.title)}</div>
      <div>${escapeHtml(r.text)}</div>
    </div>
  `).join("");
}

function escapeHtml(text){
  const div=document.createElement("div");
  div.textContent=text;
  return div.innerHTML;
}

async function refresh(){
  if(!loggedIn)return;

  try{
    const s=await api("/api/admin/state");
    render(s);
    await renderSummary();
  }catch(e){}
}

async function renderSummary(){
  const d=await api("/api/admin/summary");

  $("summary").innerHTML =
    `<div class="summary-row summary-head">
      <div>AUSSAGE</div><div>RUNDE 1</div>
    </div>` +
    d.questions.map(x=>{
      const p1=x.round1.total
        ? Math.round(x.round1.yes/x.round1.total*100)
        : 0;

      return `
        <div class="summary-row">
          <div>${x.question.id}. ${escapeHtml(x.question.text)}</div>
          <div>
            ${p1}% DAFÜR
            <div class="mini-bar"><i style="width:${p1}%"></i></div>
          </div>
        </div>`;
    }).join("");

  $("scoreGrid").innerHTML="";
  for(let i=0;i<=10;i++){
    const b=document.createElement("button");
    b.textContent=i;
    b.onclick=()=>submitScore(i);
    $("scoreGrid").appendChild(b);
  }

  $("scoreAverage").textContent =
    d.score_average===null
      ? "Noch keine Bewertungen"
      : `Klassenmittel: ${d.score_average}/10 (${d.scores.length} Stimmen)`;
}

async function submitScore(score){
  try{
    await api("/api/admin/final-score",{
      method:"POST",
      body:JSON.stringify({score})
    });
    renderSummary();
  }catch(e){
    alert(e.message);
  }
}

setInterval(refresh,1000);
