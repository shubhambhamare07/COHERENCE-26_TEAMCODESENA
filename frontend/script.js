/* ArthRakshak — Shared Data & Logic */
var NATIONWIDE=[
  {id:'n1',name:'Ayushman Bharat PM-JAY',budget:'50,000 Cr',distributed:'14,000 Cr',utilization:28,year:2018,sector:'Healthcare',riskScore:42,ministry:'Ministry of Health',beneficiaries:'10.74 Cr families',desc:'World largest govt-funded health insurance providing ₹5 lakh coverage per family for hospitalisation.'},
  {id:'n2',name:'Pradhan Mantri Awas Yojana',budget:'3,00,000 Cr',distributed:'2,20,000 Cr',utilization:73,year:2015,sector:'Housing',riskScore:31,ministry:'Ministry of Housing',beneficiaries:'2.95 Cr households',desc:'Affordable housing to urban and rural poor. Housing for All mission.'},
  {id:'n3',name:'PM-KISAN',budget:'60,000 Cr/yr',distributed:'80,000 Cr total',utilization:91,year:2019,sector:'Agriculture',riskScore:22,ministry:'Ministry of Agriculture',beneficiaries:'11.4 Cr farmers',desc:'Direct income support of ₹6,000/year to all landholding farmer families.'},
  {id:'n4',name:'MGNREGA',budget:'6,000 Cr',distributed:'—',utilization:55,year:2005,sector:'Employment',riskScore:57,ministry:'Ministry of Rural Development',beneficiaries:'5.5 Cr households',desc:'Guarantees 100 days of wage employment per year to adult rural household members.'},
  {id:'n5',name:'PM Ujjwala Yojana',budget:'12,000 Cr',distributed:'1,000 Cr',utilization:8,year:2016,sector:'Energy/Welfare',riskScore:38,ministry:'Ministry of Petroleum',beneficiaries:'9.59 Cr connections',desc:'LPG connections to women from BPL households to free them from harmful cooking fuel.'},
  {id:'n6',name:'Jan Dhan Yojana',budget:'20,000 Cr',distributed:'2 Lakh Cr deposits',utilization:82,year:2014,sector:'Financial Inclusion',riskScore:19,ministry:'Ministry of Finance',beneficiaries:'51.12 Cr accounts',desc:'National mission for financial inclusion — banking, credit, insurance and pension access.'},
  {id:'n7',name:'PM SVANidhi',budget:'5,000 Cr',distributed:'800 Cr',utilization:16,year:2020,sector:'Small Business',riskScore:44,ministry:'Ministry of Housing',beneficiaries:'61.5 Lakh vendors',desc:'Micro-credit for street vendors to provide working capital loans up to ₹50,000.'},
  {id:'n8',name:'Beti Bachao Beti Padhao',budget:'2,000 Cr',distributed:'500 Cr',utilization:25,year:2015,sector:'Social Welfare',riskScore:68,ministry:'Ministry of WCD',beneficiaries:'Pan India',desc:'Addresses declining Child Sex Ratio and women empowerment through education and welfare.'},
  {id:'n9',name:'Digital India Mission',budget:'1,30,000 Cr',distributed:'40,000 Cr',utilization:31,year:2015,sector:'Technology',riskScore:26,ministry:'Ministry of Electronics & IT',beneficiaries:'135 Cr citizens',desc:'Transform India into a digitally empowered society and knowledge economy.'},
  {id:'n10',name:'PM Surya Ghar Muft Bijli Yojana',budget:'75,000 Cr',distributed:'2,75,000 Cr',utilization:79,year:2024,sector:'Renewable Energy',riskScore:35,ministry:'Ministry of New & Renewable Energy',beneficiaries:'1 Cr households',desc:'300 units free electricity/month via rooftop solar systems for 1 crore households.'}
];
var STATE=[
  {id:'s1',name:'Mukhyamantri Majhi Ladki Bahin Yojana',budget:'29,570 Cr',utilized:'15,000 Cr',remaining:'14,570 Cr',utilization:51,state:'Maharashtra',sector:'Social Welfare',riskScore:33,purpose:'₹1,500 monthly financial support to women'},
  {id:'s2',name:'Magel Tyala Solar Pump Yojana',budget:'15,000 Cr',utilized:'7,200 Cr',remaining:'7,800 Cr',utilization:48,state:'Maharashtra',sector:'Agriculture',riskScore:41,purpose:'Solar irrigation pumps for farmers'},
  {id:'s3',name:'Mukhyamantri Yuva Karya Prashikshan Yojana',budget:'6,000 Cr',utilized:'2,900 Cr',remaining:'3,100 Cr',utilization:48,state:'Maharashtra',sector:'Employment',riskScore:55,purpose:'Youth internship stipend & skill training'},
  {id:'s4',name:'Mukhyamantri Annapurna Yojana',budget:'1,200 Cr',utilized:'620 Cr',remaining:'580 Cr',utilization:52,state:'Maharashtra',sector:'Welfare',riskScore:30,purpose:'Free LPG cylinders for poor families'},
  {id:'s5',name:'Jal Yukta Shivar Abhiyan',budget:'650 Cr',utilized:'310 Cr',remaining:'340 Cr',utilization:48,state:'Maharashtra',sector:'Water',riskScore:25,purpose:'Water conservation & drought projects'},
  {id:'s6',name:'Gaon Tithe Godown Yojana',budget:'341 Cr',utilized:'160 Cr',remaining:'181 Cr',utilization:47,state:'Maharashtra',sector:'Agriculture',riskScore:62,purpose:'Village crop storage warehouses'},
  {id:'s7',name:'Solar Rooftop SMART Scheme',budget:'655 Cr',utilized:'320 Cr',remaining:'335 Cr',utilization:49,state:'Maharashtra',sector:'Energy',riskScore:29,purpose:'Rooftop solar installation for households'},
  {id:'s8',name:'Free Higher Education Scheme for Girls',budget:'2,000 Cr',utilized:'950 Cr',remaining:'1,050 Cr',utilization:48,state:'Maharashtra',sector:'Education',riskScore:21,purpose:'Fee reimbursement for higher education'},
  {id:'s9',name:'Mahatma Phule Jan Arogya Yojana',budget:'3,282 Cr',utilized:'1,650 Cr',remaining:'1,632 Cr',utilization:50,state:'Maharashtra',sector:'Healthcare',riskScore:36,purpose:'Health insurance up to ₹5 lakh per family'},
  {id:'s10',name:'Maharashtra Irrigation Improvement Program',budget:'15,000 Cr',utilized:'7,500 Cr',remaining:'7,500 Cr',utilization:50,state:'Maharashtra',sector:'Infrastructure',riskScore:44,purpose:'Irrigation canals & water supply'}
];
var DISTRICT=[
  {id:'d1',name:'NH-60 Highway Widening Project',budget:'95 Cr',utilized:'42 Cr',remaining:'53 Cr',utilization:44,district:'Pune',town:'Shivajinagar',sector:'Roads',riskScore:52,purpose:'Highway widening 4-lane'},
  {id:'d2',name:'Wagholi-Kesnand Rural Road',budget:'7.5 Cr',utilized:'3.2 Cr',remaining:'4.3 Cr',utilization:43,district:'Pune',town:'Shivajinagar',sector:'Roads',riskScore:39,purpose:'Rural road 8 km'},
  {id:'d3',name:'Indrayani River Bridge',budget:'18 Cr',utilized:'9.5 Cr',remaining:'8.5 Cr',utilization:53,district:'Pune',town:'Shivajinagar',sector:'Infrastructure',riskScore:31,purpose:'Bridge construction'},
  {id:'d4',name:'Katraj Bus Stand Modernization',budget:'3.8 Cr',utilized:'1.5 Cr',remaining:'2.3 Cr',utilization:39,district:'Pune',town:'Shivajinagar',sector:'Transport',riskScore:67,purpose:'Bus stand development'},
  {id:'d5',name:'Pune Junction Improvement',budget:'42 Cr',utilized:'28 Cr',remaining:'14 Cr',utilization:67,district:'Pune',town:'Shivajinagar',sector:'Transport',riskScore:28,purpose:'Railway station improvement'},
  {id:'d6',name:'Hadapsar Drinking Water Pipeline',budget:'11 Cr',utilized:'6.4 Cr',remaining:'4.6 Cr',utilization:58,district:'Pune',town:'Shivajinagar',sector:'Water',riskScore:45,purpose:'Drinking water pipeline'},
  {id:'d7',name:'Manjari Water Tank',budget:'85 L',utilized:'55 L',remaining:'30 L',utilization:65,district:'Pune',town:'Shivajinagar',sector:'Water',riskScore:22,purpose:'Village water tank'},
  {id:'d8',name:'Phursungi Groundwater Recharge',budget:'18 L',utilized:'8 L',remaining:'10 L',utilization:44,district:'Pune',town:'Shivajinagar',sector:'Water',riskScore:18,purpose:'Borewell/groundwater recharge'},
  {id:'d9',name:'Mulshi Irrigation Canal',budget:'28 Cr',utilized:'15 Cr',remaining:'13 Cr',utilization:54,district:'Pune',town:'Shivajinagar',sector:'Agriculture',riskScore:49,purpose:'Irrigation canal development'},
  {id:'d10',name:'Kothrud Rainwater Harvesting',budget:'1.6 Cr',utilized:'0.9 Cr',remaining:'0.7 Cr',utilization:56,district:'Pune',town:'Shivajinagar',sector:'Water',riskScore:16,purpose:'Rainwater harvesting'}
];
var RURAL=DISTRICT.map(function(s){return Object.assign({},s,{id:s.id.replace('d','r')});});

function getUser(){try{return JSON.parse(sessionStorage.getItem('ar_user'));}catch(e){return null;}}
function requireAuth(){if(!getUser())window.location.href='login.html';}
function logout(){sessionStorage.clear();window.location.href='login.html';}

function getSchemes(user){
  if(!user)return[];
  var d=user.dept;
  if(d==='Finance Ministry'||d==='Chief Economic Advisory')return NATIONWIDE.concat(STATE).concat(DISTRICT).concat(RURAL);
  if(d==='State Department')return STATE.filter(function(s){return s.state===user.state;}).concat(DISTRICT.filter(function(s){return s.district===user.district&&s.state===user.state;})).concat(RURAL.filter(function(s){return s.town===user.town&&s.district===user.district;}));
  if(d==='District Administration')return DISTRICT.filter(function(s){return s.district===user.district;}).concat(RURAL.filter(function(s){return s.town===user.town&&s.district===user.district;}));
  if(d==='Rural Administration')return RURAL.filter(function(s){return s.town===user.town;});
  return[];
}

function riskClass(score){if(score<30)return'low';if(score<55)return'medium';if(score<75)return'high';return'critical';}
function riskLabel(score){
  if(score<30)return'Low';
  if(score<55)return'Medium';
  if(score<75)return'High';
  return'Critical';
}
function utilColor(u){return u>70?'#1a7a4a':u>40?'#e85d00':'#c0392b';}

function initTopbar(user){
  var n=document.getElementById('uname')||document.getElementById('u-name');
  var d=document.getElementById('udept')||document.getElementById('u-dept');
  var a=document.getElementById('uavatar')||document.getElementById('u-avatar');
  if(n&&user)n.textContent=user.name;
  if(d&&user)d.textContent=user.dept;
  if(a&&user)a.textContent=user.name.charAt(0);
}
function setTopbar(user){initTopbar(user);}
function schemeMapsUrl(s){var q=encodeURIComponent((s.district||s.state||'India')+' '+s.name);return 'https://www.google.com/maps/search/?api=1&query='+q;}
function downloadSchemePdf(schemeId,schemeName){var u=getUser();if(!u)return;var api=(!window.location.origin||window.location.origin==='null')?'http://localhost:5050':window.location.origin;fetch(api+'/api/pdf/scheme',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({scheme_id:schemeId,user:u})}).then(function(r){return r.blob();}).then(function(blob){var a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=(schemeName||'Scheme').substring(0,50).replace(/[^a-zA-Z0-9]/g,'_')+'.pdf';a.click();URL.revokeObjectURL(a.href);}).catch(function(){alert('PDF download failed. Ensure backend is running.');});}
