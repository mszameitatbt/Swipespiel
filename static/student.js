let lastKey = "";
let submitted = false;
let proposalLastId = null;
let proposalSubmitted = false;
let submissionSent = false;

async function getStatus(){
  const r = await fetch("/api/status", {cache:"no-store"});
  return r.json();
}

function setVoteButtons(enabled, selector=".vote"){
  document.querySelectorAll(selector).forEach(b => b.disabled = !enabled);
}

function renderWaiting(){
  document.getElementById("waiting").classList.remove("hidden");
  document.getElementById("swipeArea").classList.add("hidden");
  document.getElementById("constitutionArea").classList.add("hidden");
}

function renderSwipe(s){
  document.getElementById("waiting").classList.add("hidden");
  document.getElementById("swipeArea").classList.remove("hidden");
  document.getElementById("constitutionArea").classList.add("hidden");

  document.getElementById("progressBar").style.width =
    `${((s.question_index+1)/s.question_count)*100}%`;
  document.getElementById("counter").textContent =
    `${s.question_index+1} / ${s.question_count}`;
  document.getElementById("number").textContent =
    `AUSSAGE ${s.question.id}`;
  document.getElementById("statement").textContent =
    `„${s.question.text}“`;

  const key = `1:${s.question_index}`;
  if(key !== lastKey){
    submitted = false;
    lastKey = key;
  }

  document.getElementById("buttons").classList.toggle(
    "hidden", submitted || !s.accepting
  );
  document.getElementById("done").classList.toggle("hidden", !submitted);
  document.getElementById("revealed").classList.toggle("hidden", !s.revealed);

  setVoteButtons(!submitted && s.accepting, "#buttons .vote");

  if(s.revealed){
    const yes=s.votes.yes||0, no=s.votes.no||0, total=yes+no;
    const yp=total?Math.round(yes/total*100):0;
    const np=100-yp;
    document.getElementById("yesCount").textContent=`${yp}%`;
    document.getElementById("noCount").textContent=`${np}%`;
    document.getElementById("yesBar").style.width=`${yp}%`;
    document.getElementById("noBar").style.width=`${np}%`;
  }
}

function renderConstitution(s){
  document.getElementById("waiting").classList.add("hidden");
  document.getElementById("swipeArea").classList.add("hidden");
  document.getElementById("constitutionArea").classList.remove("hidden");

  const p = s.proposal;
  submissionSent = !!s.submission_sent;

  renderConstitutionRules(s.constitution_rules || []);

  if(!p){
    document.getElementById("proposalText").textContent =
      "Formuliere eine Regel für eure Verfassung.";
    document.getElementById("proposalStatus").textContent =
      s.submission_open
        ? "Schicke einen konkreten Vorschlag ab. Pro Gerät ist ein Vorschlag möglich."
        : "Warte, bis die Lehrkraft einen Vorschlag auswählt.";
    document.getElementById("proposalVoteButtons").classList.add("hidden");
    document.getElementById("proposalDone").classList.add("hidden");
    document.getElementById("proposalResult").classList.add("hidden");

    if(s.submission_open && !submissionSent){
      showProposalForm();
    } else {
      hideProposalForm();
    }
    return;
  }

  hideProposalForm();
  document.getElementById("proposalText").textContent = `„${p.text}“`;

  if(proposalLastId !== p.id){
    proposalLastId = p.id;
    proposalSubmitted = false;
  }

  document.getElementById("proposalVoteButtons").classList.toggle(
    "hidden", proposalSubmitted || !s.accepting
  );
  document.getElementById("proposalDone").classList.toggle(
    "hidden", !proposalSubmitted
  );
  document.getElementById("proposalResult").classList.toggle(
    "hidden", !s.revealed
  );

  if(s.accepting){
    document.getElementById("proposalStatus").textContent =
      "Soll diese Regel in eure Verfassung aufgenommen werden?";
  }else if(s.revealed){
    document.getElementById("proposalStatus").textContent =
      "Das Ergebnis ist sichtbar. Die Lehrkraft entscheidet über die Aufnahme.";
  }else{
    document.getElementById("proposalStatus").textContent =
      "Die Abstimmung wird von der Lehrkraft gestartet.";
  }

  setVoteButtons(!proposalSubmitted && s.accepting, "#proposalVoteButtons .vote");

  if(s.revealed){
    const yes=s.proposal_votes.yes||0;
    const no=s.proposal_votes.no||0;
    const total=yes+no;
    const yp=total?Math.round(yes/total*100):0;
    const np=100-yp;
    document.getElementById("proposalYesCount").textContent=`${yp}%`;
    document.getElementById("proposalNoCount").textContent=`${np}%`;
    document.getElementById("proposalYesBar").style.width=`${yp}%`;
    document.getElementById("proposalNoBar").style.width=`${np}%`;
  }
}

function showProposalForm(){
  let form = document.getElementById("proposalForm");
  if(form) return;

  form = document.createElement("div");
  form.id = "proposalForm";
  form.className = "proposal-form";
  form.innerHTML = `
    <textarea id="proposalInput"
      maxlength="240"
      placeholder="z. B. „Alle erwachsenen Bürger sollen unabhängig von ihrem Besitz wählen dürfen.“"></textarea>
    <div class="proposal-form-row">
      <span>Max. 240 Zeichen · möglichst als konkrete Regel formulieren</span>
      <button class="primary" id="submitProposalBtn">Vorschlag einreichen</button>
    </div>
    <p id="proposalError" class="error"></p>
  `;
  document.getElementById("constitutionArea").insertBefore(
    form,
    document.getElementById("proposalCard")
  );

  document.getElementById("submitProposalBtn").onclick = submitProposal;
}

function hideProposalForm(){
  const form = document.getElementById("proposalForm");
  if(form) form.remove();
}

async function submitProposal(){
  const input = document.getElementById("proposalInput");
  const error = document.getElementById("proposalError");
  const text = input.value.trim();

  try{
    const r = await fetch("/api/proposal/submit", {
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify({text})
    });
    const data = await r.json();

    if(!data.ok){
      error.textContent = data.error || "Vorschlag konnte nicht gespeichert werden.";
      return;
    }

    submissionSent = true;
    hideProposalForm();
    document.getElementById("proposalText").textContent =
      "Dein Vorschlag wurde gespeichert.";
    document.getElementById("proposalStatus").textContent =
      "Warte, bis die Lehrkraft entscheidet, welcher Vorschlag als Nächstes abgestimmt wird.";
  }catch(e){
    error.textContent = "Verbindung zum Server fehlgeschlagen.";
  }
}

function renderConstitutionRules(rules){
  const container = document.getElementById("constitutionRulesStudent");
  if(!rules.length){
    container.innerHTML =
      `<div class="empty-state">Noch keine Regel wurde beschlossen.</div>`;
    return;
  }

  container.innerHTML = rules.map(r => `
    <div class="constitution-rule">
      <strong>${r.number}.</strong>
      <span>${escapeHtml(r.text)}</span>
    </div>
  `).join("");
}

function escapeHtml(text){
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

async function vote(answer){
  if(submitted) return;
  const r=await fetch("/api/vote",{
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({answer})
  });
  const data=await r.json();
  if(data.ok){
    submitted=true;
    document.getElementById("buttons").classList.add("hidden");
    document.getElementById("done").classList.remove("hidden");
  }else{
    alert(data.error||"Abstimmung nicht möglich.");
  }
}

async function voteProposal(answer){
  if(proposalSubmitted) return;

  const r = await fetch("/api/proposal/vote", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({answer})
  });
  const data = await r.json();

  if(data.ok){
    proposalSubmitted = true;
    document.getElementById("proposalVoteButtons").classList.add("hidden");
    document.getElementById("proposalDone").classList.remove("hidden");
  }else{
    alert(data.error || "Abstimmung nicht möglich.");
  }
}

document.querySelectorAll("#buttons .vote").forEach(
  b => b.addEventListener("click",()=>vote(b.dataset.answer))
);
document.querySelectorAll("#proposalVoteButtons .vote").forEach(
  b => b.addEventListener("click",()=>voteProposal(b.dataset.answer))
);

let touchStartX=0;
const card=document.getElementById("card");

card.addEventListener("touchstart",e=>{
  touchStartX=e.changedTouches[0].screenX
},{passive:true});

card.addEventListener("touchend",e=>{
  const dx=e.changedTouches[0].screenX-touchStartX;
  if(Math.abs(dx)>80 && !submitted){
    vote(dx>0?"yes":"no");
  }
},{passive:true});

setInterval(async()=>{
  try{
    const s=await getStatus();

    if(!s.active){
      renderWaiting();
      return;
    }

    if(s.phase === "swipe") renderSwipe(s);
    if(s.phase === "constitution") renderConstitution(s);
  }catch(e){}
},700);

renderWaiting();

document.addEventListener("keydown", e => {
  if (submitted) return;
  const tag = document.activeElement?.tagName;
  if (tag === "INPUT" || tag === "TEXTAREA") return;

  if (e.key === "ArrowLeft" || e.key.toLowerCase() === "a") {
    e.preventDefault();
    if(!document.getElementById("swipeArea").classList.contains("hidden")){
      vote("no");
    }else if(!document.getElementById("constitutionArea").classList.contains("hidden")
             && !document.getElementById("proposalVoteButtons").classList.contains("hidden")){
      voteProposal("no");
    }
  }

  if (e.key === "ArrowRight" || e.key.toLowerCase() === "d") {
    e.preventDefault();
    if(!document.getElementById("swipeArea").classList.contains("hidden")){
      vote("yes");
    }else if(!document.getElementById("constitutionArea").classList.contains("hidden")
             && !document.getElementById("proposalVoteButtons").classList.contains("hidden")){
      voteProposal("yes");
    }
  }
});
