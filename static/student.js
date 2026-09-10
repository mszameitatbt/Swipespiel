let lastKey = "";
let submitted = false;

async function getStatus(){
  const r = await fetch("/api/status", {cache:"no-store"});
  return r.json();
}

function setVoteButtons(enabled){
  document.querySelectorAll(".vote").forEach(b => b.disabled = !enabled);
}

function render(s){
  const waiting = document.getElementById("waiting");
  const area = document.getElementById("voteArea");
  if(!s.active || !s.question){
    waiting.classList.remove("hidden"); area.classList.add("hidden"); return;
  }
  waiting.classList.add("hidden"); area.classList.remove("hidden");

  document.getElementById("roundPill").textContent = `RUNDE ${s.round}`;
  document.getElementById("progressBar").style.width = `${((s.question_index+1)/s.question_count)*100}%`;
  document.getElementById("counter").textContent = `${s.question_index+1} / ${s.question_count}`;
  document.getElementById("number").textContent = `AUSSAGE ${s.question.id}`;
  document.getElementById("statement").textContent = `„${s.question.text}“`;
  document.getElementById("hint").textContent = s.question.hint || "";

  const key = `${s.round}:${s.question_index}`;
  if(key !== lastKey){ submitted = false; lastKey = key; }
  document.getElementById("buttons").classList.toggle("hidden", submitted || !s.accepting);
  document.getElementById("done").classList.toggle("hidden", !submitted && s.accepting);
  document.getElementById("done").classList.toggle("hidden", !submitted);
  document.getElementById("revealed").classList.toggle("hidden", !s.revealed);
  setVoteButtons(!submitted && s.accepting);

  if(s.revealed){
    const yes=s.votes.yes||0, no=s.votes.no||0, total=yes+no;
    const yp=total?Math.round(yes/total*100):0, np=100-yp;
    document.getElementById("yesCount").textContent=`${yp}%`;
    document.getElementById("noCount").textContent=`${np}%`;
    document.getElementById("yesBar").style.width=`${yp}%`;
    document.getElementById("noBar").style.width=`${np}%`;
  }
}

async function vote(answer){
  if(submitted) return;
  const r=await fetch("/api/vote",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({answer})});
  const data=await r.json();
  if(data.ok){
    submitted=true;
    document.getElementById("buttons").classList.add("hidden");
    document.getElementById("done").classList.remove("hidden");
  }else alert(data.error||"Abstimmung nicht möglich.");
}
document.querySelectorAll(".vote").forEach(b=>b.addEventListener("click",()=>vote(b.dataset.answer)));

let touchStartX=0;
const card=document.getElementById("card");
card.addEventListener("touchstart",e=>touchStartX=e.changedTouches[0].screenX,{passive:true});
card.addEventListener("touchend",e=>{
  const dx=e.changedTouches[0].screenX-touchStartX;
  if(Math.abs(dx)>80 && !submitted){
    vote(dx>0?"yes":"no");
  }
},{passive:true});

setInterval(async()=>{ try{render(await getStatus())}catch(e){} },700);
render({active:false});

document.addEventListener("keydown", e => {
  if (submitted) return;

  // Ignore keys while typing into an input/textarea.
  const tag = document.activeElement?.tagName;
  if (tag === "INPUT" || tag === "TEXTAREA") return;

  if (e.key === "ArrowLeft" || e.key.toLowerCase() === "a") {
    e.preventDefault();
    vote("no");
  }

  if (e.key === "ArrowRight" || e.key.toLowerCase() === "d") {
    e.preventDefault();
    vote("yes");
  }
});
