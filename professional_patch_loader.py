from pathlib import Path
import re

ROOT = Path("Ask_MASTIC_V11_RENDER_SAFE")
TARGET = ROOT / "platform" / "index.html"
APP = ROOT / "backend" / "app.py"
CSS = Path("professional_ui.css")
SECTION = Path("professional_section.html")
UI_MARKER = "mastic-professional-loader-v1"

def patch_html():
    if not TARGET.exists() or not CSS.exists() or not SECTION.exists():
        return
    html = TARGET.read_text(encoding="utf-8", errors="ignore")
    if UI_MARKER in html:
        return

    css = CSS.read_text(encoding="utf-8", errors="ignore")
    section = SECTION.read_text(encoding="utf-8", errors="ignore")

    extra_css = r"""
<style id="mastic-professional-loader-v1">
html,body{overflow-x:hidden}
body.mp-professional-open #professionalTalentSection{display:block!important}
body.mp-professional-open #mpModuleGrid{display:none!important}
body.mp-professional-open main > *:not(#professionalTalentSection):not(script):not(style){display:none!important}
body.mp-home-clean [data-mp-hide-home="1"]{display:none!important}
body.mp-home-clean #mpModuleGrid{display:block!important}
body.mp-home-clean footer{margin-top:6px!important}
@media(min-width:900px){
  body.mp-home-clean{overflow-y:hidden!important}
  body.mp-home-clean main{min-height:calc(100vh - 120px)!important}
  body.mp-home-clean #mpModuleGrid{padding-bottom:2px!important}
}
</style>
"""

    js = r"""
<script id="mastic-professional-loader-v1-js">
(function(){
  const norm=s=>String(s||'').replace(/\s+/g,' ').trim();

  function findExact(label){
    return [...document.querySelectorAll('button,a,h1,h2,h3,h4,h5,span,div,p')]
      .find(el=>norm(el.textContent)===label);
  }
  function findNav(label){
    return [...document.querySelectorAll('nav a,nav button,.nav a,.nav button,[role="tab"]')]
      .find(el=>norm(el.textContent).includes(label));
  }
  function hideLegacyBlock(label){
    const el=findExact(label);
    if(!el) return;
    let box=el.closest('section,[class*="card"],[class*="panel"],[class*="box"],[class*="block"]');
    if(!box) box=el.parentElement;
    if(box && box!==document.body && box!==document.querySelector('main')){
      box.dataset.mpHideHome='1';
    }
  }
  function ensureHome(){
    document.body.classList.remove('mp-professional-open');
    document.body.classList.add('mp-home-clean');
    document.querySelectorAll('nav .active,.nav .active,[role="tab"].active').forEach(x=>x.classList.remove('active'));
  }
  function openProfessional(){
    document.body.classList.remove('mp-home-clean');
    document.body.classList.add('mp-professional-open');
    document.querySelectorAll('nav .active,.nav .active,[role="tab"].active').forEach(x=>x.classList.remove('active'));
    document.getElementById('mpProfessionalNav')?.classList.add('active');
    window.scrollTo(0,0);
  }
  function activateExisting(label){
    document.body.classList.remove('mp-professional-open');
    document.body.classList.remove('mp-home-clean');
    const n=findNav(label);
    if(n) n.click();
  }
  function build(){
    const main=document.querySelector('main');
    const prof=document.getElementById('professionalTalentSection');
    const grid=document.getElementById('mpModuleGrid');
    if(!main || !prof || !grid) return;

    if(prof.parentElement!==main) main.appendChild(prof);

    const hero=findExact('Memahami Rantaian Bakat STEM');
    let heroBlock=hero ? hero.closest('section,[class*="hero"]') : null;
    if(!heroBlock && hero) heroBlock=hero.parentElement;
    if(heroBlock && grid.previousElementSibling!==heroBlock){
      heroBlock.insertAdjacentElement('afterend',grid);
    } else if(grid.parentElement!==main) {
      main.insertBefore(grid,main.firstChild);
    }

    ['Analitik Sedia Ada','Apabila Data Diseragam dan Dihubungkan','Isyarat Dasar','Laluan ke arah Inteligen Bakat'].forEach(hideLegacyBlock);

    /* Remove the entire legacy three-column explanatory infographic from Ringkasan. */
    const legacyNeedles=['Analitik Sedia Ada','Penyeragaman','Di mana jurang bakat muncul?'];
    const legacyCandidates=[...document.querySelectorAll('main section, main > div, main div')].filter(el=>{
      const t=norm(el.textContent);
      return legacyNeedles.every(x=>t.includes(x));
    });
    if(legacyCandidates.length){
      legacyCandidates.sort((a,b)=>a.textContent.length-b.textContent.length);
      let legacy=legacyCandidates[0];
      while(legacy.parentElement && legacy.parentElement!==main){
        const pt=norm(legacy.parentElement.textContent);
        if(!legacyNeedles.every(x=>pt.includes(x))) break;
        if(legacy.parentElement.children.length>1) break;
        legacy=legacy.parentElement;
      }
      legacy.dataset.mpHideHome='1';
      legacy.style.display='none';
    }

    const grad=findNav('Graduan & Pasaran Kerja');
    if(grad && !document.getElementById('mpProfessionalNav')){
      const n=grad.cloneNode(true);
      n.id='mpProfessionalNav';
      n.removeAttribute('href');
      n.textContent='Bakat Profesional';
      n.addEventListener('click',e=>{e.preventDefault();e.stopPropagation();openProfessional();});
      grad.insertAdjacentElement('afterend',n);
    }

    document.querySelectorAll('#mpModuleGrid [data-mptarget]').forEach(btn=>{
      btn.addEventListener('click',()=>activateExisting(btn.dataset.mptarget));
    });
    document.querySelector('#mpModuleGrid [data-mpprof]')?.addEventListener('click',openProfessional);

    document.querySelectorAll('#professionalTalentSection .mp-tab').forEach(btn=>{
      btn.addEventListener('click',()=>{
        document.querySelectorAll('#professionalTalentSection .mp-tab').forEach(x=>x.classList.toggle('active',x===btn));
        document.querySelectorAll('#professionalTalentSection .mp-view').forEach(v=>v.classList.toggle('active',v.id==='mp-'+btn.dataset.mpview));
      });
    });

    document.querySelectorAll('nav a,nav button,.nav a,.nav button,[role="tab"]').forEach(n=>{
      if(n.id==='mpProfessionalNav') return;
      if(norm(n.textContent).includes('Ringkasan')){
        n.addEventListener('click',()=>setTimeout(ensureHome,0));
      }else{
        n.addEventListener('click',()=>{document.body.classList.remove('mp-professional-open');document.body.classList.remove('mp-home-clean');},true);
      }
    });

    ensureHome();
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',build); else build();
})();
</script>
"""

    html = html.replace("</head>", "<style>\n"+css+"\n</style>\n"+extra_css+"\n</head>", 1)
    html = html.replace("</body>", section+"\n"+js+"\n</body>", 1)
    TARGET.write_text(html, encoding="utf-8")

def patch_backend():
    if not APP.exists():
        return
    txt = APP.read_text(encoding="utf-8", errors="ignore")
    marker = "# MASTIC_PROFESSIONAL_QA_V1"
    if marker in txt:
        return

    needle = "    # Fast factual route."
    if needle not in txt:
        return

    block = r"""
    # MASTIC_PROFESSIONAL_QA_V1
    bem_source={'title':'Laporan Tahunan BEM 2023','source':'BEM','url':'https://bem.org.my/uploads/Resource/Publication/BEM_Annual_Report_2023.pdf'}
    mbot_source={'title':'Laporan Tahunan MBOT 2024','source':'MBOT','url':'https://www.mbot.org.my/getattachment/144d2637-9399-4952-8a03-3f14da10d71c/Annual-Report-2024'}

    if ('bakat profesional' in ql or ('bem' in ql and 'mbot' in ql)):
        answer=('Modul Bakat Profesional menggabungkan dua registry profesional yang saling melengkapi. '
                'BEM memberi gambaran pipeline kejuruteraan melalui GE, PE dan PEPC serta disiplin utama, '
                'manakala MBOT menunjukkan pipeline teknologis dan juruteknik melalui GT, Ts., QT dan Tc. '
                'Kedua-duanya ialah signal sisi penawaran dan profesionalisme; penilaian kekurangan atau lebihan sebenar masih perlu dipadankan dengan data permintaan industri.')
        return JSONResponse({'answer':answer,'sources':[bem_source,mbot_source],'route':'local:professional-combined','confidence':'high','llm_used':False},status_code=200)

    if ('bem' in ql or 'lembaga jurutera' in ql or 'graduate engineer' in ql or 'pepc' in ql):
        if any(x in ql for x in ('disiplin','bidang','awam','civil','mekanikal','mechanical','elektrikal','electrical','kimia','chemical')):
            answer=('Berdasarkan Laporan Tahunan BEM 2023, 195,521 Graduate Engineer berdaftar terdiri daripada '
                    '59,909 Kejuruteraan Awam, 54,984 Elektrikal, 54,576 Mekanikal, 25,979 Kimia dan 73 lain-lain. '
                    'Tiga disiplin terbesar ialah Awam, Elektrikal dan Mekanikal. Angka ini ialah rekod pendaftaran BEM dan tidak semestinya mewakili tenaga kerja aktif.')
        else:
            answer=('Berdasarkan Laporan Tahunan BEM 2023, BEM merekodkan 195,521 Graduate Engineer, 23,595 Professional Engineer '
                    '(termasuk PEPC), 10,788 PEPC, 15,269 Engineering Technologist dan 9,782 Inspector of Works. '
                    'Struktur ini sesuai dibaca sebagai baseline pipeline profesional; kadar peralihan GE ke PE sebenar memerlukan data longitudinal individu.')
        return JSONResponse({'answer':answer,'sources':[bem_source],'route':'local:bem-professional','confidence':'high','llm_used':False},status_code=200)

    if ('mbot' in ql or 'teknologis' in ql or 'technologist' in ql or 'juruteknik bertauliah' in ql or 'certified technician' in ql):
        if any(x in ql for x in ('bidang','field','teknologi apa','technology field')):
            answer=('Laporan Tahunan MBOT 2024 menonjolkan pelbagai bidang melalui program dan aktiviti, antaranya Electrical & Electronic, '
                    'Information & Communication Technology, Green Technology, Manufacturing & Industrial, Aerospace & Aviation, '
                    'Building & Construction, Oil & Gas, Biotechnology, Maritime serta Telecommunication & Broadcasting. '
                    'Laporan tersebut tidak memberikan agihan jumlah pendaftar yang lengkap mengikut setiap bidang, jadi bidang ini tidak wajar ditafsir sebagai ranking bilangan bakat.')
        else:
            answer=('Berdasarkan Laporan Tahunan MBOT 2024, jumlah pendaftaran mencapai 95,630 orang: 56,501 Teknologis Berijazah, '
                    '23,705 Teknologis Profesional (Ts.), 12,208 Juruteknik Berkelayakan dan 3,216 Juruteknik Bertauliah (Tc.). '
                    'Jumlah pendaftaran keseluruhan meningkat daripada 1,842 pada 2017 kepada 95,630 pada 2024. '
                    'Data ini menunjukkan pertumbuhan registry profesional yang pesat, tetapi kadar peralihan individu GT→Ts. atau QT→Tc. memerlukan data cohort.')
        return JSONResponse({'answer':answer,'sources':[mbot_source],'route':'local:mbot-professional','confidence':'high','llm_used':False},status_code=200)

"""
    txt = txt.replace(needle, block+"\n"+needle, 1)
    APP.write_text(txt, encoding="utf-8")

try:
    patch_html()
    patch_backend()
except Exception as e:
    print("[professional_patch_loader]", repr(e))
