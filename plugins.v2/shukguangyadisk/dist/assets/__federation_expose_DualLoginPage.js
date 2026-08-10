import OldPage from './__federation_expose_Page-3595592a.js';
import { importShared } from './__federation_fn_import-054b33c3.js';

const { defineComponent, h, ref } = await importShared('vue');

async function apiPost(props, path, body) {
  const apiPath = `plugin/GuangyaDisk${path}`;
  if (props.api?.post) {
    return props.api.post(apiPath, body || {});
  }
  const response = await fetch(`/api/v1/plugin/GuangyaDisk${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body || {}),
  });
  return response.json();
}

const DualLoginPage = defineComponent({
  name: 'DualLoginPage',
  props: {
    initialConfig: { type: Object, default: () => ({}) },
    api: { type: Object, default: () => ({}) },
  },
  emits: ['close', 'switch'],
  setup(props, { emit }) {
    const mode = ref('qr');
    const phone = ref('');
    const code = ref('');
    const verificationId = ref('');
    const sending = ref(false);
    const logging = ref(false);
    const message = ref('');
    const messageType = ref('');

    const sendCode = async () => {
      if (!phone.value.trim()) {
        messageType.value = 'error';
        message.value = '请输入手机号';
        return;
      }
      sending.value = true;
      message.value = '';
      try {
        const result = await apiPost(props, '/login/sms/send', { phone_number: phone.value.trim() });
        if (!result?.success) throw new Error(result?.message || '发送验证码失败');
        verificationId.value = result.verification_id || '';
        messageType.value = 'success';
        message.value = '验证码已发送，请查收短信';
      } catch (err) {
        messageType.value = 'error';
        message.value = err?.message || '发送验证码失败';
      } finally {
        sending.value = false;
      }
    };

    const login = async () => {
      if (!phone.value.trim() || !code.value.trim()) {
        messageType.value = 'error';
        message.value = '请输入手机号和验证码';
        return;
      }
      logging.value = true;
      message.value = '';
      try {
        const result = await apiPost(props, '/login/sms/verify', {
          phone_number: phone.value.trim(),
          verification_code: code.value.trim(),
          verification_id: verificationId.value,
        });
        if (!result?.success) throw new Error(result?.message || '短信登录失败');
        messageType.value = 'success';
        message.value = '登录成功，正在切回账号页面';
        setTimeout(() => { mode.value = 'qr'; }, 600);
      } catch (err) {
        messageType.value = 'error';
        message.value = err?.message || '短信登录失败';
      } finally {
        logging.value = false;
      }
    };

    const buttonStyle = (active) => ({
      flex: '1',
      border: '1px solid rgba(var(--v-theme-on-surface),0.14)',
      borderRadius: '10px',
      padding: '10px 14px',
      cursor: 'pointer',
      fontWeight: active ? '700' : '500',
      background: active ? 'rgba(var(--v-theme-primary),0.14)' : 'rgba(var(--v-theme-surface),0.5)',
      color: 'rgb(var(--v-theme-on-surface))',
    });

    return () => h('div', { style: { width: '100%' } }, [
      h('div', {
        style: {
          display: 'flex', gap: '10px', padding: '12px 16px 0', maxWidth: '520px', margin: '0 auto',
        },
      }, [
        h('button', { style: buttonStyle(mode.value === 'qr'), onClick: () => { mode.value = 'qr'; message.value = ''; } }, '扫码登录'),
        h('button', { style: buttonStyle(mode.value === 'sms'), onClick: () => { mode.value = 'sms'; message.value = ''; } }, '短信登录'),
      ]),
      mode.value === 'qr'
        ? h(OldPage, {
            initialConfig: props.initialConfig,
            api: props.api,
            onClose: () => emit('close'),
            onSwitch: () => emit('switch'),
          })
        : h('div', {
            style: {
              maxWidth: '520px', margin: '18px auto', padding: '24px',
              borderRadius: '16px', border: '1px solid rgba(var(--v-theme-on-surface),0.12)',
              background: 'rgb(var(--v-theme-surface))',
            },
          }, [
            h('div', { style: { fontSize: '20px', fontWeight: '700', marginBottom: '6px' } }, '手机号短信登录'),
            h('div', { style: { opacity: '.7', fontSize: '13px', marginBottom: '20px' } }, '如果扫码环境受限，可使用光鸭云盘账号绑定手机号完成登录。'),
            h('label', { style: { display: 'block', fontSize: '13px', marginBottom: '6px' } }, '手机号'),
            h('input', {
              value: phone.value,
              onInput: e => { phone.value = e.target.value; },
              placeholder: '请输入手机号，例如 13800000000',
              style: { width: '100%', boxSizing: 'border-box', padding: '11px 12px', borderRadius: '9px', border: '1px solid #9995', marginBottom: '14px', background: 'transparent', color: 'inherit' },
            }),
            h('label', { style: { display: 'block', fontSize: '13px', marginBottom: '6px' } }, '短信验证码'),
            h('div', { style: { display: 'flex', gap: '8px', marginBottom: '16px' } }, [
              h('input', {
                value: code.value,
                onInput: e => { code.value = e.target.value; },
                placeholder: '验证码',
                style: { flex: '1', minWidth: '0', padding: '11px 12px', borderRadius: '9px', border: '1px solid #9995', background: 'transparent', color: 'inherit' },
              }),
              h('button', { disabled: sending.value, onClick: sendCode, style: { padding: '0 14px', borderRadius: '9px', border: '1px solid #9995', cursor: 'pointer' } }, sending.value ? '发送中...' : '发送验证码'),
            ]),
            h('button', {
              disabled: logging.value,
              onClick: login,
              style: { width: '100%', padding: '11px 14px', border: '0', borderRadius: '9px', cursor: 'pointer', fontWeight: '700', background: 'rgb(var(--v-theme-primary))', color: 'rgb(var(--v-theme-on-primary))' },
            }, logging.value ? '登录中...' : '登录'),
            message.value ? h('div', { style: { marginTop: '14px', fontSize: '13px', color: messageType.value === 'error' ? '#ef4444' : '#10b981' } }, message.value) : null,
            h('div', { style: { marginTop: '18px', fontSize: '12px', opacity: '.65', lineHeight: '1.7' } }, '扫码登录仍为推荐方式。短信登录仅作为备用入口，两种方式最终都会保存 access_token 与 refresh_token。'),
          ]),
    ]);
  },
});

export default DualLoginPage;
