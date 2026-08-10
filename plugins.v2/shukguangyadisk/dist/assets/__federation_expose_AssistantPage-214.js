import OldPage from './__federation_expose_Page-3595592a.js';
import { importShared } from './__federation_fn_import-054b33c3.js';

const { defineComponent, h, ref, reactive, computed, onMounted, onBeforeUnmount, nextTick } = await importShared('vue');
const PLUGIN_ID = 'ShukGuangYaDisk';

function rewritePluginPath(path) {
  return String(path || '').replace(/^plugin\/GuangyaDisk/, `plugin/${PLUGIN_ID}`);
}
function createApiProxy(api) {
  if (!api) return api;
  return {
    ...api,
    get: api.get ? ((path, options) => api.get(rewritePluginPath(path), options)) : undefined,
    post: api.post ? ((path, body, options) => api.post(rewritePluginPath(path), body, options)) : undefined,
    put: api.put ? ((path, body, options) => api.put(rewritePluginPath(path), body, options)) : undefined,
    delete: api.delete ? ((path, options) => api.delete(rewritePluginPath(path), options)) : undefined,
  };
}
async function apiGet(props, path) {
  const apiPath = `plugin/${PLUGIN_ID}${path}`;
  if (props.api?.get) return props.api.get(apiPath);
  const response = await fetch(`/api/v1/plugin/${PLUGIN_ID}${path}`);
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}
async function apiPost(props, path, body = {}) {
  const apiPath = `plugin/${PLUGIN_ID}${path}`;
  if (props.api?.post) return props.api.post(apiPath, body);
  const response = await fetch(`/api/v1/plugin/${PLUGIN_ID}${path}`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}
function fmtSize(value) {
  let n = Number(value || 0);
  if (!n) return '0 B';
  const units = ['B','KB','MB','GB','TB','PB'];
  let i = 0;
  while (n >= 1024 && i < units.length - 1) { n /= 1024; i += 1; }
  return `${n.toFixed(n >= 100 || i === 0 ? 0 : n >= 10 ? 1 : 2)} ${units[i]}`;
}
function maskPhone(v) {
  const s = String(v || '');
  if (s.length >= 7) return `${s.slice(0,3)}****${s.slice(-4)}`;
  return s || '-';
}

const styles = `
.gya-root{width:100%;box-sizing:border-box;color:rgb(var(--v-theme-on-surface));font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif}
.gya-wrap{width:min(100%,760px);margin:0 auto;padding:10px;box-sizing:border-box}
.gya-shell{width:100%;border:1px solid rgba(var(--v-theme-on-surface),.075);border-radius:16px;background:rgb(var(--v-theme-surface));box-shadow:0 8px 24px rgba(0,0,0,.045);overflow:hidden}
.gya-header{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:14px 16px;border-bottom:1px solid rgba(var(--v-theme-on-surface),.06)}
.gya-brand{display:flex;align-items:center;gap:10px;min-width:0}.gya-logo{width:38px;height:38px;border-radius:11px;background:linear-gradient(135deg,rgba(var(--v-theme-primary),.18),rgba(var(--v-theme-primary),.07));display:flex;align-items:center;justify-content:center;color:rgb(var(--v-theme-primary));font-size:20px;flex:none}
.gya-title{font-size:16px;font-weight:760;line-height:1.2}.gya-version{display:inline-flex;margin-left:6px;padding:2px 6px;border-radius:999px;background:rgba(var(--v-theme-primary),.1);color:rgb(var(--v-theme-primary));font-size:9px;vertical-align:2px}.gya-sub{margin-top:3px;font-size:10.5px;color:rgba(var(--v-theme-on-surface),.48)}
.gya-actions{display:flex;gap:6px;flex:none}.gya-iconbtn{width:32px;height:32px;border:1px solid rgba(var(--v-theme-on-surface),.09);border-radius:9px;background:rgba(var(--v-theme-on-surface),.02);color:rgb(var(--v-theme-on-surface));font-size:14px;cursor:pointer}
.gya-content{padding:12px}.gya-stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px;margin-bottom:10px}.gya-stat{padding:9px 10px;border:1px solid rgba(var(--v-theme-on-surface),.065);border-radius:10px;background:rgba(var(--v-theme-on-surface),.012)}.gya-stat-label{font-size:9.5px;color:rgba(var(--v-theme-on-surface),.46);margin-bottom:3px}.gya-stat-value{font-size:12.5px;font-weight:730;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.ok{color:#10b981}.warn{color:#f59e0b}.primary{color:rgb(var(--v-theme-primary))}
.gya-main{display:grid;grid-template-columns:minmax(0,1.04fr) minmax(260px,.96fr);gap:10px;align-items:start}.gya-card{border:1px solid rgba(var(--v-theme-on-surface),.07);border-radius:12px;background:rgba(var(--v-theme-on-surface),.009);padding:12px}.gya-card+.gya-card{margin-top:9px}.gya-card-title{font-size:12.5px;font-weight:730;margin-bottom:2px}.gya-card-sub{font-size:10px;color:rgba(var(--v-theme-on-surface),.48);margin-bottom:9px}
.gya-select{width:100%;height:35px;border:1px solid rgba(var(--v-theme-on-surface),.11);border-radius:8px;padding:0 9px;background:rgb(var(--v-theme-surface));color:rgb(var(--v-theme-on-surface));font-size:11.5px;outline:none;margin-bottom:9px}
.gya-qrbox{min-height:224px;border:1px dashed rgba(var(--v-theme-on-surface),.13);border-radius:10px;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:10px;box-sizing:border-box;background:rgba(var(--v-theme-on-surface),.008)}.gya-qrimg{width:178px;height:178px;max-width:64vw;max-height:64vw;object-fit:contain;background:#fff;border-radius:7px;padding:4px;box-sizing:border-box}.gya-qrplaceholder{font-size:11px;color:rgba(var(--v-theme-on-surface),.46)}.gya-qrhint{font-size:10px;color:rgba(var(--v-theme-on-surface),.5);margin-top:8px;text-align:center}.gya-qractions{display:flex;justify-content:center;gap:7px;margin-top:8px}
.gya-btn{height:33px;padding:0 11px;border-radius:8px;border:1px solid rgba(var(--v-theme-on-surface),.11);background:rgb(var(--v-theme-surface));color:rgb(var(--v-theme-on-surface));font-size:11px;cursor:pointer}.gya-btn.primarybtn{border-color:transparent;background:rgb(var(--v-theme-primary));color:rgb(var(--v-theme-on-primary));font-weight:650}.gya-btn.danger{color:#ef4444;border-color:rgba(239,68,68,.2);background:rgba(239,68,68,.035)}
.gya-form{display:grid;gap:8px}.gya-field label{display:block;font-size:10px;color:rgba(var(--v-theme-on-surface),.5);margin-bottom:4px}.gya-input{width:100%;height:36px;box-sizing:border-box;border:1px solid rgba(var(--v-theme-on-surface),.11);border-radius:8px;padding:0 9px;background:rgb(var(--v-theme-surface));color:rgb(var(--v-theme-on-surface));font-size:11.5px;outline:none}.gya-code-row{display:grid;grid-template-columns:minmax(0,1fr) 92px;gap:7px}.gya-msg{font-size:10.5px;padding:7px 9px;border-radius:7px;background:rgba(16,185,129,.07);color:#10b981}.gya-msg.error{background:rgba(239,68,68,.07);color:#ef4444}
.gya-login-ok{display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;min-height:150px;padding:8px}.gya-check{width:48px;height:48px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:rgba(16,185,129,.1);color:#10b981;font-size:28px;margin-bottom:8px}.gya-login-ok strong{font-size:14px}.gya-login-ok p{font-size:10.5px;line-height:1.6;color:rgba(var(--v-theme-on-surface),.5);margin:5px 0 10px}
.gya-info-grid{display:grid;grid-template-columns:1fr 1fr;gap:0 12px}.gya-info{padding:7px 0;border-bottom:1px solid rgba(var(--v-theme-on-surface),.05);min-width:0}.gya-info-k{font-size:9.5px;color:rgba(var(--v-theme-on-surface),.44);margin-bottom:2px}.gya-info-v{font-size:11.5px;font-weight:620;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.gya-space-head{display:flex;align-items:flex-end;justify-content:space-between;gap:8px;margin-bottom:7px}.gya-space-big{font-size:16px;font-weight:760}.gya-space-pct{font-size:10px;color:rgba(var(--v-theme-on-surface),.46)}.gya-bar{height:6px;background:rgba(var(--v-theme-on-surface),.065);border-radius:999px;overflow:hidden;margin-bottom:7px}.gya-bar>i{display:block;height:100%;border-radius:999px;background:rgb(var(--v-theme-primary))}.gya-space-row{display:flex;justify-content:space-between;font-size:10px;color:rgba(var(--v-theme-on-surface),.54);line-height:1.7}
.gya-note{margin-top:9px;padding:8px 9px;border-radius:8px;background:rgba(var(--v-theme-primary),.05);font-size:9.8px;line-height:1.55;color:rgba(var(--v-theme-on-surface),.56)}
.gya-footer{display:flex;justify-content:space-between;gap:8px;padding:8px 14px;border-top:1px solid rgba(var(--v-theme-on-surface),.055);font-size:9px;color:rgba(var(--v-theme-on-surface),.36)}
.gya-engine{position:fixed!important;left:-12000px!important;top:-12000px!important;width:360px!important;height:360px!important;opacity:0!important;pointer-events:none!important;overflow:hidden!important}
@media(max-width:700px){.gya-wrap{padding:6px}.gya-shell{border-radius:13px}.gya-header{padding:11px 12px}.gya-logo{width:35px;height:35px}.gya-title{font-size:15px}.gya-sub{display:none}.gya-content{padding:9px}.gya-stats{grid-template-columns:1fr 1fr;gap:6px}.gya-main{grid-template-columns:1fr;gap:8px}.gya-card{padding:10px}.gya-qrbox{min-height:216px}.gya-qrimg{width:170px;height:170px}.gya-footer{padding:8px 10px;flex-direction:column;gap:2px}}
@media(max-width:420px){.gya-header{gap:7px}.gya-brand{gap:8px}.gya-logo{width:32px;height:32px;border-radius:9px}.gya-title{font-size:14px}.gya-actions{gap:4px}.gya-iconbtn{width:30px;height:30px}.gya-stat{padding:8px}.gya-stat-value{font-size:11.5px}.gya-info-grid{grid-template-columns:1fr}.gya-code-row{grid-template-columns:1fr}.gya-code-row .gya-btn{width:100%}.gya-qrimg{width:162px;height:162px}}
`;

const AssistantPage = defineComponent({
  name: 'GuangyaCloudAssistantDev',
  props: { initialConfig: { type: Object, default: () => ({}) }, api: { type: Object, default: () => ({}) } },
  emits: ['close','switch'],
  setup(props,{emit}) {
    const mode = ref('qr');
    const hiddenKey = ref(1);
    const engineHost = ref(null);
    const qrSrc = ref('');
    const phone = ref('');
    const code = ref('');
    const verificationId = ref('');
    const sending = ref(false);
    const logging = ref(false);
    const refreshing = ref(false);
    const message = ref('');
    const messageType = ref('');
    const status = reactive({enabled:false,logged_in:false,user_name:'',user_id:'',phone:'',email:'',vip_level:'',total_space:0,used_space:0,free_space:0,file_count:0,poll_interval:5,page_size:100});
    const proxiedApi = createApiProxy(props.api);
    let timer = null;
    let observer = null;

    const usagePct = computed(() => status.total_space ? Math.min(100, Math.max(0, Math.round(status.used_space / status.total_space * 1000) / 10)) : 0);
    const clearMsg = () => { message.value=''; messageType.value=''; };

    async function refreshStatus() {
      refreshing.value = true;
      try {
        const data = await apiGet(props,'/config');
        Object.assign(status, {
          enabled:Boolean(data?.enabled), logged_in:Boolean(data?.logged_in), user_name:data?.user_name||'', user_id:data?.user_id||'', phone:data?.phone||data?.mobile||'', email:data?.email||'', vip_level:data?.vip_level||'',
          total_space:Number(data?.total_space||0), used_space:Number(data?.used_space||0), free_space:Number(data?.free_space||0), file_count:Number(data?.file_count||0), poll_interval:Number(data?.poll_interval||5), page_size:Number(data?.page_size||100)
        });
      } catch (_) {} finally { refreshing.value = false; }
    }
    function scanQrFromEngine() {
      const root = engineHost.value;
      if (!root) return;
      const img = root.querySelector('img.gy-qrcode-image, img[alt*="二维码"], .gy-qrcode-box img, img');
      if (img?.src && img.src !== qrSrc.value) qrSrc.value = img.src;
    }
    function bindEngineObserver() {
      if (observer) observer.disconnect();
      if (!engineHost.value) return;
      observer = new MutationObserver(() => scanQrFromEngine());
      observer.observe(engineHost.value,{subtree:true,childList:true,attributes:true,attributeFilter:['src']});
      scanQrFromEngine();
    }
    async function reloadQr() {
      qrSrc.value=''; hiddenKey.value += 1; await nextTick(); bindEngineObserver();
    }
    async function sendCode() {
      if (!phone.value.trim()) { messageType.value='error'; message.value='请输入手机号'; return; }
      sending.value=true; clearMsg();
      try {
        const r=await apiPost(props,'/login/sms/send',{phone_number:phone.value.trim()});
        if(!r?.success) throw new Error(r?.message||'发送失败');
        verificationId.value=r.verification_id||''; messageType.value='success'; message.value='验证码已发送';
      } catch(e){messageType.value='error';message.value=e?.message||'发送失败';} finally {sending.value=false;}
    }
    async function smsLogin() {
      if(!phone.value.trim()||!code.value.trim()){messageType.value='error';message.value='请输入手机号和验证码';return;}
      logging.value=true; clearMsg();
      try{
        const r=await apiPost(props,'/login/sms/verify',{phone_number:phone.value.trim(),verification_code:code.value.trim(),verification_id:verificationId.value});
        if(!r?.success) throw new Error(r?.message||'登录失败');
        messageType.value='success';message.value='登录成功';await refreshStatus();
      }catch(e){messageType.value='error';message.value=e?.message||'登录失败';}finally{logging.value=false;}
    }
    async function logout() {
      try { await apiPost(props,'/login/logout',{}); qrSrc.value=''; await refreshStatus(); if(mode.value==='qr') await reloadQr(); } catch(_) {}
    }

    onMounted(async()=>{
      await refreshStatus();
      await nextTick();
      if(!status.logged_in && mode.value==='qr') bindEngineObserver();
      timer=setInterval(()=>{refreshStatus();scanQrFromEngine();},2500);
    });
    onBeforeUnmount(()=>{if(timer)clearInterval(timer);if(observer)observer.disconnect();});

    const info=(k,v)=>h('div',{class:'gya-info'},[h('div',{class:'gya-info-k'},k),h('div',{class:'gya-info-v',title:String(v||'-')},v||'-')]);
    const stat=(label,value,cls='')=>h('div',{class:'gya-stat'},[h('div',{class:'gya-stat-label'},label),h('div',{class:`gya-stat-value ${cls}`},value)]);

    const smsForm=()=>h('div',{class:'gya-form'},[
      h('div',{class:'gya-field'},[h('label',null,'手机号'),h('input',{class:'gya-input',value:phone.value,onInput:e=>phone.value=e.target.value,inputmode:'tel',autocomplete:'tel',placeholder:'请输入绑定手机号'})]),
      h('div',{class:'gya-field'},[h('label',null,'验证码'),h('div',{class:'gya-code-row'},[
        h('input',{class:'gya-input',value:code.value,onInput:e=>code.value=e.target.value,inputmode:'numeric',autocomplete:'one-time-code',placeholder:'请输入验证码'}),
        h('button',{class:'gya-btn',disabled:sending.value,onClick:sendCode},sending.value?'发送中…':'获取验证码')
      ])]),
      message.value?h('div',{class:`gya-msg ${messageType.value==='error'?'error':''}`},message.value):null,
      h('button',{class:'gya-btn primarybtn',disabled:logging.value,onClick:smsLogin},logging.value?'登录中…':'短信登录')
    ]);

    const qrPanel=()=>h('div',null,[
      h('div',{class:'gya-qrbox'},[
        qrSrc.value?h('img',{class:'gya-qrimg',src:qrSrc.value,alt:'光鸭云盘登录二维码'}):h('div',{class:'gya-qrplaceholder'},'二维码加载中…'),
        h('div',{class:'gya-qrhint'},'打开光鸭云盘 App → 扫一扫 → 确认登录')
      ]),
      h('div',{class:'gya-qractions'},[h('button',{class:'gya-btn',onClick:reloadQr},'刷新二维码')])
    ]);

    const loginCard=()=>h('div',{class:'gya-card'},[
      h('div',{class:'gya-card-title'},status.logged_in?'授权状态':'登录方式'),
      h('div',{class:'gya-card-sub'},status.logged_in?'当前账号已完成授权，存储服务可直接使用':'扫码和短信共用同一登录区域'),
      status.logged_in
        ? h('div',{class:'gya-login-ok'},[
            h('div',{class:'gya-check'},'✓'),
            h('strong',null,'已登录'),
            h('p',null,'光鸭云盘授权有效，目录浏览与整理上传可直接使用。'),
            h('button',{class:'gya-btn danger',onClick:logout},'退出登录')
          ])
        : h('div',null,[
            h('select',{class:'gya-select',value:mode.value,onChange:async e=>{mode.value=e.target.value;clearMsg();if(mode.value==='qr'){await nextTick();bindEngineObserver();}}},[
              h('option',{value:'qr'},'扫码登录'),h('option',{value:'sms'},'短信登录')
            ]),
            mode.value==='qr'?qrPanel():smsForm()
          ])
    ]);

    const userCard=()=>h('div',{class:'gya-card'},[
      h('div',{class:'gya-card-title'},'用户信息'),
      h('div',{class:'gya-card-sub'},status.logged_in?'当前授权账号':'登录后自动显示账号信息'),
      h('div',{class:'gya-info-grid'},[
        info('用户名',status.user_name||'-'),info('用户 ID',status.user_id||'-'),info('手机号',maskPhone(status.phone)),info('会员信息',status.vip_level||'普通用户')
      ])
    ]);

    const spaceCard=()=>h('div',{class:'gya-card'},[
      h('div',{class:'gya-card-title'},'空间使用'),
      h('div',{class:'gya-space-head'},[h('div',{class:'gya-space-big'},`${fmtSize(status.used_space)} / ${fmtSize(status.total_space)}`),h('div',{class:'gya-space-pct'},`${usagePct.value}%`)]),
      h('div',{class:'gya-bar'},[h('i',{style:{width:`${usagePct.value}%`}})]),
      h('div',{class:'gya-space-row'},[h('span',null,'已用空间'),h('span',null,fmtSize(status.used_space))]),
      h('div',{class:'gya-space-row'},[h('span',null,'剩余空间'),h('span',null,fmtSize(status.free_space))]),
      h('div',{class:'gya-space-row'},[h('span',null,'文件数量'),h('span',null,String(status.file_count||0))])
    ]);

    return ()=>h('div',{class:'gya-root'},[
      h('style',null,styles),
      h('div',{class:'gya-wrap'},[
        h('div',{class:'gya-shell'},[
          h('div',{class:'gya-header'},[
            h('div',{class:'gya-brand'},[
              h('div',{class:'gya-logo'},'☁'),
              h('div',null,[h('div',{class:'gya-title'},['光鸭云盘助手',h('span',{class:'gya-version'},'v2.2.15')]),h('div',{class:'gya-sub'},'MoviePilot 光鸭云盘存储插件')])
            ]),
            h('div',{class:'gya-actions'},[
              h('button',{class:'gya-iconbtn',title:'刷新状态',onClick:refreshStatus},refreshing.value?'…':'↻'),
              h('button',{class:'gya-iconbtn',title:'设置',onClick:()=>emit('switch')},'⚙'),
              h('button',{class:'gya-iconbtn',title:'关闭',onClick:()=>emit('close')},'×')
            ])
          ]),
          h('div',{class:'gya-content'},[
            h('div',{class:'gya-stats'},[
              stat('登录状态',status.logged_in?'在线':'离线',status.logged_in?'ok':'warn'),
              stat('插件状态',status.enabled?'已启用':'未启用',status.enabled?'ok':'warn'),
              stat('空间使用',status.total_space?fmtSize(status.used_space):'-','primary'),
              stat('授权方式',status.logged_in?'已授权':(mode.value==='qr'?'扫码登录':'短信登录'),'primary')
            ]),
            h('div',{class:'gya-main'},[
              h('div',null,[loginCard()]),
              h('div',null,[userCard(),spaceCard()])
            ]),
            !status.logged_in?h('div',{class:'gya-note'},'登录完成后，插件会自动保存授权信息并启用光鸭云盘存储。无需在设置页手动填写 Token。'):null
          ]),
          h('div',{class:'gya-footer'},[h('span',null,'光鸭云盘助手 · MoviePilot 存储插件'),h('span',null,'扫码 / 短信 · 目录浏览 · 整理上传')])
        ])
      ]),
      (!status.logged_in && mode.value==='qr')?h('div',{class:'gya-engine',ref:engineHost},[
        h(OldPage,{key:hiddenKey.value,initialConfig:props.initialConfig,api:proxiedApi,onClose:()=>{},onSwitch:()=>{}})
      ]):null
    ]);
  }
});

export default AssistantPage;
