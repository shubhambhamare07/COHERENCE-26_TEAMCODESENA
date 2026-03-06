/* ArthRakshak — Shared Data & Utilities */
'use strict';

const NATIONWIDE=[
  {id:'n1',name:'Ayushman Bharat PM-JAY',budget:'₹50,000 Cr',distributed:'₹14,000 Cr',utilization:28,year:2018,sector:'Healthcare',desc:'World\'s largest government health insurance — ₹5 lakh cover per family for secondary & tertiary hospitalization.',ministry:'Ministry of Health & Family Welfare',beneficiaries:'10.74 Cr families',riskScore:42},
  {id:'n2',name:'PM Awas Yojana (PMAY)',budget:'₹3,00,000 Cr',distributed:'₹2,20,000 Cr',utilization:73,year:2015,sector:'Housing',desc:'Affordable housing to urban and rural poor. Housing for All Mission by 2024.',ministry:'Ministry of Housing & Urban Affairs',beneficiaries:'2.95 Cr households',riskScore:31},
  {id:'n3',name:'PM-KISAN',budget:'₹60,000 Cr/yr',distributed:'₹80,000 Cr total',utilization:91,year:2019,sector:'Agriculture',desc:'Direct income support of ₹6,000/year to all landholding farmer families.',ministry:'Ministry of Agriculture & Farmers Welfare',beneficiaries:'11.4 Cr farmers',riskScore:22},
  {id:'n4',name:'MGNREGA',budget:'₹6,000 Cr',distributed:'—',utilization:55,year:2005,sector:'Employment',desc:'Guarantees 100 days of wage employment per financial year to rural adult household members.',ministry:'Ministry of Rural Development',beneficiaries:'5.5 Cr households',riskScore:57},
  {id:'n5',name:'PM Ujjwala Yojana',budget:'₹12,000 Cr',distributed:'₹1,000 Cr',utilization:8,year:2016,sector:'Energy/Welfare',desc:'Free LPG connections to BPL women households — cleaner cooking fuel.',ministry:'Ministry of Petroleum & Natural Gas',beneficiaries:'9.59 Cr connections',riskScore:38},
  {id:'n6',name:'Jan Dhan Yojana',budget:'₹20,000 Cr',distributed:'₹2 Lakh Cr deposits',utilization:82,year:2014,sector:'Financial Inclusion',desc:'National financial inclusion mission — banking, credit, insurance and pension access.',ministry:'Ministry of Finance',beneficiaries:'51.12 Cr accounts',riskScore:19},
  {id:'n7',name:'PM SVANidhi',budget:'₹5,000 Cr',distributed:'₹800 Cr',utilization:16,year:2020,sector:'Small Business',desc:'Micro-credit for street vendors — working capital loans up to ₹50,000.',ministry:'Ministry of Housing & Urban Affairs',beneficiaries:'61.5 Lakh vendors',riskScore:44},
  {id:'n8',name:'Beti Bachao Beti Padhao',budget:'₹2,000 Cr',distributed:'₹500 Cr',utilization:25,year:2015,sector:'Social Welfare',desc:'Addresses declining Child Sex Ratio and women empowerment through awareness and education.',ministry:'Ministry of Women & Child Development',beneficiaries:'Pan India',riskScore:68},
  {id:'n9',name:'Digital India Mission',budget:'₹1,30,000 Cr',distributed:'₹40,000 Cr',utilization:31,year:2015,sector:'Technology',desc:'Transform India into a digitally empowered society and knowledge economy.',ministry:'Ministry of Electronics & IT',beneficiaries:'135 Cr citizens',riskScore:26},
  {id:'n10',name:'PM Surya Ghar Muft Bijli',budget:'₹75,000 Cr',distributed:'₹2,75,000 Cr',utilization:79,year:2024,sector:'Renewable Energy',desc:'300 units free electricity/month via rooftop solar — targeting 1 crore households.',ministry:'Ministry of New & Renewable Energy',beneficiaries:'1 Cr households (target)',riskScore:35}
];

const STATE=[
  {id:'s1',name:'Majhi Ladki Bahin Yojana',budget:'₹29,570 Cr',utilized:'₹15,000 Cr',remaining:'₹14,570 Cr',state:'Maharashtra',purpose:'₹1,500 monthly financial support to women',sector:'Social Welfare',utilization:51,riskScore:33},
  {id:'s2',name:'Magel Tyala Solar Pump Yojana',budget:'₹15,000 Cr',utilized:'₹7,200 Cr',remaining:'₹7,800 Cr',state:'Maharashtra',purpose:'Solar irrigation pumps for farmers',sector:'Agriculture',utilization:48,riskScore:41},
  {id:'s3',name:'Yuva Karya Prashikshan Yojana',budget:'₹6,000 Cr',utilized:'₹2,900 Cr',remaining:'₹3,100 Cr',state:'Maharashtra',purpose:'Youth internship stipend & skill training',sector:'Employment',utilization:48,riskScore:55},
  {id:'s4',name:'Mukhyamantri Annapurna Yojana',budget:'₹1,200 Cr',utilized:'₹620 Cr',remaining:'₹580 Cr',state:'Maharashtra',purpose:'Free LPG cylinders for poor families',sector:'Welfare',utilization:52,riskScore:30},
  {id:'s5',name:'Jal Yukta Shivar Abhiyan',budget:'₹650 Cr',utilized:'₹310 Cr',remaining:'₹340 Cr',state:'Maharashtra',purpose:'Water conservation & drought projects',sector:'Water',utilization:48,riskScore:25},
  {id:'s6',name:'Gaon Tithe Godown Yojana',budget:'₹341 Cr',utilized:'₹160 Cr',remaining:'₹181 Cr',state:'Maharashtra',purpose:'Village crop storage warehouses',sector:'Agriculture',utilization:47,riskScore:62},
  {id:'s7',name:'Solar Rooftop SMART Scheme',budget:'₹655 Cr',utilized:'₹320 Cr',remaining:'₹335 Cr',state:'Maharashtra',purpose:'Rooftop solar for households',sector:'Energy',utilization:49,riskScore:29},
  {id:'s8',name:'Free Higher Education for Girls',budget:'₹2,000 Cr',utilized:'₹950 Cr',remaining:'₹1,050 Cr',state:'Maharashtra',purpose:'Fee reimbursement for higher education',sector:'Education',utilization:48,riskScore:21},
  {id:'s9',name:'Mahatma Phule Jan Arogya Yojana',budget:'₹3,282 Cr',utilized:'₹1,650 Cr',remaining:'₹1,632 Cr',state:'Maharashtra',purpose:'Health insurance up to ₹5 lakh per family',sector:'Healthcare',utilization:50,riskScore:36},
  {id:'s10',name:'Maharashtra Irrigation Program',budget:'₹15,000 Cr',utilized:'₹7,500 Cr',remaining:'₹7,500 Cr',state:'Maharashtra',purpose:'Irrigation canals & water supply',sector:'Infrastructure',utilization:50,riskScore:44}
];

const DISTRICT=[
  {id:'d1',name:'NH-60 Highway Widening Project',budget:'₹95 Cr',utilized:'₹42 Cr',remaining:'₹53 Cr',district:'Pune',town:'Shivajinagar',purpose:'4-lane highway widening',sector:'Roads',utilization:44,riskScore:52},
  {id:'d2',name:'Wagholi-Kesnand Rural Road',budget:'₹7.5 Cr',utilized:'₹3.2 Cr',remaining:'₹4.3 Cr',district:'Pune',town:'Shivajinagar',purpose:'Rural road between villages (8 km)',sector:'Roads',utilization:43,riskScore:39},
  {id:'d3',name:'Indrayani River Bridge',budget:'₹18 Cr',utilized:'₹9.5 Cr',remaining:'₹8.5 Cr',district:'Pune',town:'Shivajinagar',purpose:'Bridge construction over Indrayani',sector:'Infrastructure',utilization:53,riskScore:31},
  {id:'d4',name:'Katraj Bus Stand Modernization',budget:'₹3.8 Cr',utilized:'₹1.5 Cr',remaining:'₹2.3 Cr',district:'Pune',town:'Shivajinagar',purpose:'Bus stand development',sector:'Transport',utilization:39,riskScore:67},
  {id:'d5',name:'Pune Junction Improvement',budget:'₹42 Cr',utilized:'₹28 Cr',remaining:'₹14 Cr',district:'Pune',town:'Shivajinagar',purpose:'Railway station improvement',sector:'Transport',utilization:67,riskScore:28},
  {id:'d6',name:'Hadapsar Drinking Water Pipeline',budget:'₹11 Cr',utilized:'₹6.4 Cr',remaining:'₹4.6 Cr',district:'Pune',town:'Shivajinagar',purpose:'Drinking water pipeline',sector:'Water',utilization:58,riskScore:45},
  {id:'d7',name:'Manjari Village Water Tank',budget:'₹85 L',utilized:'₹55 L',remaining:'₹30 L',district:'Pune',town:'Shivajinagar',purpose:'Village water tank construction',sector:'Water',utilization:65,riskScore:22},
  {id:'d8',name:'Phursungi Groundwater Recharge',budget:'₹18 L',utilized:'₹8 L',remaining:'₹10 L',district:'Pune',town:'Shivajinagar',purpose:'Borewell/groundwater recharge',sector:'Water',utilization:44,riskScore:18},
  {id:'d9',name:'Mulshi Irrigation Canal',budget:'₹28 Cr',utilized:'₹15 Cr',remaining:'₹13 Cr',district:'Pune',town:'Shivajinagar',purpose:'Irrigation canal development',sector:'Agriculture',utilization:54,riskScore:49},
  {id:'d10',name:'Kothrud Rainwater Harvesting',budget:'₹1.6 Cr',utilized:'₹0.9 Cr',remaining:'₹0.7 Cr',district:'Pune',town:'Shivajinagar',purpose:'Rainwater harvesting initiative',sector:'Water',utilization:56,riskScore:16}
];

const RURAL=DISTRICT.map(s=>({...s,id:s.id.replace('d','r')}));

function getUser(){try{return JSON.parse(sessionStorage.getItem('ar_user'));}catch{return null;}}
function requireAuth(){if(!getUser())window.location.href='login.html';}
function logout(){sessionStorage.clear();window.location.href='login.html';}

function getSchemes(user){
  if(!user)return[];
  const d=user.dept;
  if(d==='Finance Ministry'||d==='Chief Economic Advisory')return NATIONWIDE;
  if(d==='State Department')return STATE.filter(s=>s.state===user.state);
  if(d==='District Administration')return DISTRICT.filter(s=>s.district===user.district);
  if(d==='Rural Administration')return RURAL.filter(s=>s.town===user.town);
  return[];
}

function levelLabel(user){
  if(!user)return'';
  const d=user.dept;
  if(d==='Finance Ministry'||d==='Chief Economic Advisory')return'National';
  if(d==='State Department')return user.state;
  if(d==='District Administration')return user.district+' District';
  if(d==='Rural Administration')return user.town;
  return'';
}

function riskClass(score){return score<30?'low':score<55?'medium':score<75?'high':'critical';}
function riskLabel(score){return score<30?'Low':score<55?'Medium':score<75?'High':'Critical';}

function setTopbar(user){
  const n=document.getElementById('u-name')||document.getElementById('uname');
  const d=document.getElementById('u-dept')||document.getElementById('udept');
  const a=document.getElementById('u-avatar')||document.getElementById('uavatar');
  if(n&&user)n.textContent=user.name;
  if(d&&user)d.textContent=user.dept;
  if(a&&user)a.textContent=user.name.charAt(0);
}

function progressColor(pct){return pct>=70?'#1a7a4a':pct>=40?'#e85d00':'#c0392b';}