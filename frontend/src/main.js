import Vue from 'vue'
import App from './App.vue'
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'
import axios from 'axios'

Vue.config.productionTip = false

// 使用Element UI
Vue.use(ElementUI)

// 配置axios - 使用环境变量
axios.defaults.baseURL = process.env.VUE_APP_API_BASE_URL || 'http://localhost:5000'

new Vue({
  render: h => h(App),
}).$mount('#app') 