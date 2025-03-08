import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import 'element-plus/dist/index.css'; // 引入样式
import ElementPlus from 'element-plus'; // 引入组件库
import * as ElIcons from '@element-plus/icons-vue'; // 引入图标组件

const app = createApp(App);
app.use(ElementPlus); // 注册组件库
app.use(router);

// 全局注册图标组件
Object.keys(ElIcons).forEach((key) => {
  app.component(key, ElIcons[key]);
});

app.mount('#app');
