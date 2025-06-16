import Vue from 'vue'
import App from './App.vue'
import ElementUI from 'element-ui';
import 'element-ui/lib/theme-chalk/index.css';
import router from './router'
import axios from 'axios'
import VueRouter from "vue-router";
import "echarts";
import ECharts from "vue-echarts/dist/index.esm";
// import ECharts from "vue-echarts";

Vue.prototype.$axios=axios;
Vue.prototype.$httpUrl='http://localhost:8000';

Vue.use(VueRouter)
Vue.use(ElementUI, {size:'small'})
import { codemirror } from 'vue-codemirror'
import 'codemirror/lib/codemirror.css';
import 'codemirror/theme/material.css';
import 'codemirror/mode/python/python.js';

Vue.use(codemirror)
Vue.component('ECharts', ECharts)
Vue.config.productionTip = false;
new Vue({
    render: h => h(App),
    router: router
}).$mount('#app')
