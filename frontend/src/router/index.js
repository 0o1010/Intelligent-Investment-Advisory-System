import VueRouter from 'vue-router'
import Login from "@/pages/Login";
import Index from "@/components/Index";
import Visualization from "@/components/Visualization";
import LLM from "@/components/LLM";
import Suggestion from "@/components/Suggestion";
import Modify from "@/components/Modify";

export default new VueRouter({
    mode: 'history',
    routes: [
        {
            path: '/',
            component: Login,
            meta: {
                title: 'Login'
            },
        },
        {
            path: '/login',
            component: Login,
            meta: {
                title: 'Login'
            },
        },
        {
            path: '/register',
            component: () => import('@/pages/Register'),
            meta: {
                title: 'Register'
            },
        },

        {
            path: '/index',
            component: Index,
            meta: {
                title: 'Index'
            },
            children: [
                {
                    path: '/main',
                    meta: {
                        title: 'Visualization'
                    },
                    component: Visualization
                },
                {
                    path: '/llm',
                    meta: {
                        title: 'LLM'
                    },
                    component: LLM
                },
                {
                    path: '/suggestion',
                    meta: {
                        title: 'Suggestion'
                    },
                    component: Suggestion
                },
                {
                    path: '/modify',
                    meta: {
                        title: 'Modify info'
                    },
                    component: Modify
                },

            ]
        },
    ]
})
